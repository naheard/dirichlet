#! /usr/bin/env python
import sys
import argparse
from collections import Counter
from numpy import loadtxt, log
global alpha,k,n,num_categories,alpha_star,ranks,category_counts

parser = argparse.ArgumentParser()
parser.add_argument("-a","--alpha",type=float,dest="alpha", metavar="FLOAT",default=1.0)
parser.add_argument("-k","--classes",type=int,dest="k", metavar="INT",default=0)
args = parser.parse_args()
alpha=args.alpha
k=args.k

def reset():
    global alpha,k,n,num_categories,alpha_star,ranks,category_counts
    category_counts=Counter()
    ranks=[]
    num_categories=0
    alpha_star=alpha
    n=0

def dp_pvalue(x):
    global alpha,k,n,num_categories,alpha_star,ranks,category_counts
    if x not in ranks:
        cum_alpha=alpha
        if k>0:
            cum_alpha*=(k-num_categories)/float(k)
        right_pvalue=cum_alpha/alpha_star
        left_pvalue=0
        category_counts[x]=1
        ranks.append(x)
        old_rank=len(ranks)-1
        num_categories+=1
    else:
        prev_freq=category_counts[x]
        total=0
        rank=0 ##look down from top rank
        while prev_freq<category_counts[ranks[rank]]:
            total+=category_counts[ranks[rank]]
            rank+=1
        if k>0:
            total+=alpha*rank/float(k)
        tie_total=0
        lower_rank=rank
        while lower_rank<num_categories and prev_freq==category_counts[ranks[lower_rank]]:
            tie_total+=category_counts[ranks[lower_rank]]
            if x==ranks[lower_rank]:
                current_rank=lower_rank
            lower_rank+=1
        if k>0:
            tie_total+=alpha*(lower_rank-rank)/float(k)
        cum_alpha=alpha_star-total
        right_pvalue=cum_alpha/alpha_star
        left_pvalue=(cum_alpha-tie_total)/alpha_star
        category_counts[x]+=1
        new_rank=current_rank
        while new_rank>0 and category_counts[ranks[new_rank-1]]==prev_freq:
            new_rank-=1
        if new_rank < current_rank:
            ranks.insert(new_rank,ranks.pop(current_rank))
    n+=1
    alpha_star+=1
    return left_pvalue,right_pvalue

def dp_pvalues(xs):
    reset()
    min_pval=1
    for x in xs:
        pval=dp_pvalue(x)
        print x, pval
        min_pval=min(min_pval,.5*sum(pval))
        
    return 1-(1-min_pval)**len(xs)
        
xs=loadtxt(sys.stdin,dtype='str',ndmin=1)
if len(xs)==1:
    xs=xs[0]
dp=dp_pvalues(xs)
print "p-value of minimum mid p-value="+str(dp)

