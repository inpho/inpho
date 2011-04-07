/***************************************************************************
                          apriori.h  -  description
                             -------------------
    begin                : cs dec 26 2002
    copyright            : (C) 2002 by Ferenc Bodon
    email                : bodon@mit.bme.hu
 ***************************************************************************/

#ifndef APRIORI_H
#define APRIORI_H

#include "Apriori_Trie.hpp"
#include <map>


/**
  *@author Bodon Ferenc
  */

/** This class implements the APRIORI algirithm.

<p>
APRIORI is a levelwise algorithm.
It scans the transaction database several times.
After the first scan the frequent 1-itemsets are found, and in general 
after the <em>k<sup>th</sup></em> scan the frequent <em>k</em>-itemsets 
are extracted. The method does not determine the support of every possible
itemset. In an attempt to narrow the domain to be searched, before every pass 
it generates <em>candidate</em> itemsets. An itemset becomes a candidate 
if every subset of it is frequent. Obviously every frequent itemset 
needs to be candidate too, hence only the support of candidates is calculated.
Frequent <em>k</em>-itemsets generate the candidate <em>k+1</em>-itemsets 
after the \f$k^{th}\f$ scan.
</p>

<p>
After all the candidate <em>k+1</em>-itemsets have been generated, a new 
scan of the transactions is effected and the precise support of the 
candidates is determined. The candidates with low support are thrown away. The 
algorithm ends when no candidates can be generated.
</p>

<p>
The intuition behind candidate generation is based on the following simple 
fact:<br><div align="center"><em>Every subset of a frequent itemset 
is frequent.</em></div><br> This is immediate, because if a transaction 
<em>t</em> supports an itemset <em>X</em>, then <em>t</em> supports 
every subset \f$Y\subseteq X\f$.
</p>

<p>
Using the fact indirectly, we infer, that if an itemset has a subset that is 
infrequent, then it cannot be frequent. So in the algorithm APRIORI only those 
itemsets will be candidates whose every subset is frequent. The frequent 
<em>k</em>-itemsets are available when we attempt to generate candidate 
<em>k+1</em>-itemsets. The algorithm seeks candidate <em>k+1</em>-itemsets 
among the sets which are unions of two frequent <em>k</em>-itemsets. After 
forming the union we need to verify that all of its subsets are frequent, 
otherwise it should not be a candidate. To this end, it is clearly enough to 
check if all the <em>k</em>-subsets of <em>X</em> are frequent.
</p>

<p>
Next the supports of the candidates are calculated. This is done by reading 
transactions one by one. For each transaction <em>t</em> the algorithm decides 
which candidates are supported by <em>t</em>. To solve this task efficiently 
APRIORI uses a hash-tree. However in this implementation a trie (prefix-tree) 
is applied. Tries have many advantages over hash-trees.
<ol>
  <li> It is faster </li>
  <li> It needs no parameters (main drawback of a hash-tree is that its 
  performance is very sensitive to the parameteres) </li>
  <li> The candidate generation is very simple. </li>
</ol>
</p>
*/

class Apriori {
public:
   Apriori( ifstream& basket_file, const char* output_file_name, 
	    const bool store_input );

   /// This procedure implements the APRIORI algorithm
   void APRIORI_alg( const double min_supp, const double min_conf, 
		     const bool quiet, const unsigned long size_threshold );
   ~Apriori();
private:

   /// Determines the support of the candidates of the given size
   void support( const itemtype& candidate_size );

protected:
   // No protected class data members

private:
   /// A trie that stores the frequent itemset and candidates.
   Apriori_Trie*                           apriori_trie;
   /// The input_output_manager that is responsibel for the input, 
   /// output and recoding operations.
   Input_Output_Manager                    input_output_manager;
   /// This will store the reduced baskets, if store_input=true;
   map<vector<itemtype>, unsigned long>    reduced_baskets;
   /// If store_input = true, then the reduced baskets 
   /// will be stored in memory
   bool                                    store_input;
};

#endif
