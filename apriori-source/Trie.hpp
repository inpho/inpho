/***************************************************************************
                          Trie.hpp  -  description
                             -------------------
    begin                : cs dec 26 2002
    copyright            : (C) 2002 by Ferenc Bodon
    email                : bodon@mit.bme.hu
 ***************************************************************************/

#ifndef Trie_HPP
#define Trie_HPP

/**
  *@author Ferenc Bodon
  */

#include "common.hpp"
#include <vector>
#include <set>

using namespace std;

class Apriori_Trie;
class Trie;

/** This struct represent an edge of a Trie.

An edge has a label, and an edge points to a subtrie.
*/
struct Edge
{
   itemtype label;
   Trie* subtrie;
};

/** This class represent a general Trie.

   We can regard the trie as a recursive data structure. It has a root 
   node and a list of (sub)trie. We can reach a subtree by a 
   labeled edge (link). Since the root of the trie represents an itemset 
   the counter stands for the occurrence. For the sake of fast traversal 
   we also store the length of the maximal path 
   starting from the root, and the edges are stored ordered according 
   to their label.
*/

class Trie
{
friend class Apriori_Trie;

public:

   Trie( const unsigned long init_counter );

   /// It decides whether the given itemset is included in the trie or not.
   const Trie* is_included( const set<itemtype>& an_itemset, 
			    set<itemtype>::const_iterator item_it ) const;

   /// Increases the counter for those itemsets that is 
   /// contained by the given basket.
   void find_candidate( vector<itemtype>::const_iterator it_basket_upper_bound, 
			const itemtype distance_from_candidate,
			vector<itemtype>::const_iterator it_basket, 
			const unsigned long counter_incr=1);

   /// Deletes the tries that represent infrequent itemsets.
   void delete_infrequent( const double min_occurrence, 
			   const itemtype distance_from_candidate );

   /// Shows the content in a preorder manner
   void show_content_preorder( ) const;
   ~Trie();

private:

   /// Adds an empty state to the trie
   void add_empty_state( const itemtype item, 
			 const unsigned long init_counter=0 );

public:
   // No public members

private:

   /// counter stores the occurrence of the itemset represented by the Trie
   unsigned long counter;

   /** edgevector stores the edges of the root the trie.
     *
     * edgevector is always sorted!
     */
   vector<Edge> edgevector;
   
   /// maxpath stores the length of the longest path 
   /// starting from the root node.
   itemtype maxpath;
};


#endif
