/***************************************************************************
                          Apriori_Trie.hpp  -  description
                             -------------------
    begin                : cs dec 26 2002
    copyright            : (C) 2002 by Ferenc Bodon
    email                : bodon@mit.bme.hu
 ***************************************************************************/

#ifndef Apriori_Trie_HPP
#define Apriori_Trie_HPP

/**
  *@author Ferenc Bodon
  */

#include "Trie.hpp"
#include "Input_Output_Manager.hpp"
#include <fstream>
#include <set>
#include <vector>
#include <cstdio>
using namespace std;


/** Apriori_Trie (or prefix-tree) is a tree-based datastructure.

   Apriori_Trie is a special tree designed to provide efficient methods 
   for the apriori algorithm. It mostly uses a regular trie except 
   when there exist faster solution. For example for storing one and two 
   itemset candidate where a simple vector and array gives better performance.
   Apriori_Trie extends the functions provided by the regular trie with 
   a candidate generation process.

*/
class Apriori_Trie
{
public:

   Apriori_Trie( const unsigned long counter_of_emptyset );
   
   /// Insert the frequent items and their counters into the trie;
   void insert_frequent_items(const vector<unsigned long>& counters );
   
   /// Generates candidates.
   void candidate_generation( const itemtype& frequent_size );

   /// Increases the counter of those candidates that are contained 
   /// by the given basket.
   void find_candidate( const vector<itemtype>& basket, 
			const itemtype candidate_size, 
			const unsigned long counter=1 );

   /// Deletes unfrequent itemsets.
   void delete_infrequent( const double min_occurrence, 
			   const itemtype candidate_size );

   /// Generates association rules
   void association( const double min_conf, 
		     Input_Output_Manager& input_output_manager ) const;

   /// Returns the length of the longest path in the Apriori_Trie
   itemtype longest_path() const;

   /// Writes the content (frequent itemsets) to the file
   void write_content_to_file( Input_Output_Manager& input_output_manager ) const;

   /// This procedure shows the Apriori_Trie in a preorde
   void show_content_preorder( ) const;

   ~Apriori_Trie();

protected:

   /// Decides if all subset of an itemset is contained in the Apriori_Trie
   bool is_all_subset_frequent( const set<itemtype>& maybe_candidate ) const;

   /// Generates candidate of size two
   void candidate_generation_two();

   /// Generates candidate of size more than two
   void candidate_generation_assist( Trie* Trie, 
				     const itemtype distance_from_generator,
				     set<itemtype>& maybe_candidate );

   /// Increases the counter for those itempairs that are in the given basket.
   void find_candidate_two( const vector<itemtype>& basket, 
			    const unsigned long counter=1 );

   /// Deletes the Tries that represent infrequent itemsets of size 2.
   void delete_infrequent_two( const double min_occurrence );


   void assoc_rule_find( const double min_conf, set<itemtype>& condition_part, 
			 set<itemtype>& consequence_part, 
			 const unsigned long union_support, 
			 Input_Output_Manager& input_output_manager ) const;

   void assoc_rule_assist( const double min_conf, const Trie* Trie, 
			   set<itemtype>& consequence_part, 
			   Input_Output_Manager& input_output_manager ) const;

   // Writes out the content of the Apriori_Trie
   /// (frequent itemset and counters).
   void write_content_to_file_assist( Input_Output_Manager& input_output_manager, 
				      const Trie* actual_state, 
				      const itemtype distance_from_frequent, 
				      set<itemtype>& frequent_itemset ) const;
private:
   // No private methods

public:
   // No public members

protected:
   /// Trie to store the candidates and the frequent itemsets
   Trie main_trie;

   /**  temp_counter_array stores the occurences of the itempairs
     *
     * We can use a simple array to determine the support of itemset 
     * of size two. This requires less memory than the trie-based supportcount.
     * temp_counter_array[i][j-i] stores the occurence of the itempair (i,j).
     */
   vector< vector<unsigned long> > temp_counter_array;
};

#endif
