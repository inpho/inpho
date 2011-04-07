/***************************************************************************
                          Apriori_Trie.cpp  -  description
                             -------------------
    begin                : cs dec 26 2002
    copyright            : (C) 2002 by Ferenc Bodon
    email                : bodon@mit.bme.hu
 ***************************************************************************/


#include "Apriori_Trie.hpp"
#include <cstdlib>
#include <algorithm>
#include <iostream>
#include <math.h>

/**
  \param counter_of_emptyset The support of the empty set, 
                             i.e. the number of transactions.
*/
Apriori_Trie::Apriori_Trie(const unsigned long counter_of_emptyset ):
   main_trie(counter_of_emptyset)
{
}

/**
  \param counters It stores the support of the items.
                  counters[i] stores the suport of item i.
*/
void Apriori_Trie::insert_frequent_items(
   const vector<unsigned long>& counters )
{
   for(vector<unsigned long>::size_type item_index = 0; 
       item_index < counters.size(); item_index++)
      main_trie.add_empty_state( item_index, counters[item_index] );
   if( !main_trie.edgevector.empty() ) main_trie.maxpath = 1;
}

/**
  \param frequent_size Size of the frequent itemsets that 
                       generate the candidates.
*/
void Apriori_Trie::candidate_generation( const itemtype& frequent_size )
{
   if( frequent_size == 1 ) candidate_generation_two();
   else if( main_trie.maxpath == frequent_size )
   {
      set<itemtype> maybe_candidate;
      candidate_generation_assist( &main_trie, frequent_size-1, 
				   maybe_candidate );
   }
}

/**
  \param basket The basket that hs to be analyzed.
  \param candidate_size the size of the candidates.
  \param counter_incr The number of time the basket occured.
                      The counters of candidates that occure in the basket has 
		      to be incremented by counter_incr.
*/
void Apriori_Trie::find_candidate( const vector<itemtype>& basket, 
				   const itemtype candidate_size, 
				   const unsigned long counter_incr)
{
   if( candidate_size != 2 ) 
      if ( candidate_size<basket.size()+1 )
	 main_trie.find_candidate( basket.end()-candidate_size+1, candidate_size, 
				   basket.begin(), counter_incr );
      else;
   else find_candidate_two( basket, counter_incr );    
}

/**
  \param min_occurrence The threshold of absolute support.
  \param candidate_size The size of the candidate itemset.
*/
void Apriori_Trie::delete_infrequent( const double min_occurrence, 
				      const itemtype candidate_size )
{
   if( candidate_size != 2 ) 
      main_trie.delete_infrequent( min_occurrence, candidate_size - 1 );
   else delete_infrequent_two( min_occurrence );
}

/**
  \param min_conf Confidence threshold.
  \param input_output_manager This will write out itemsets.
*/
void Apriori_Trie::association( 
   const double min_conf, Input_Output_Manager& input_output_manager ) const
{
   //input_output_manager << "\nAssociation rules:\ncondition ==>";
  // input_output_manager << "consequence (confidence, occurrence)\n";
   set<itemtype> consequence_part;
   assoc_rule_assist( min_conf, &main_trie, 
		      consequence_part, input_output_manager );
}

itemtype Apriori_Trie::longest_path() const
{
	return main_trie.maxpath;
}

void Apriori_Trie::write_content_to_file( 
   Input_Output_Manager& input_output_manager ) const
{
  // input_output_manager<< "Frequent 0-itemsets:\nitemset (occurrence)\n";
  // input_output_manager<< "{} ("<< main_trie.counter << ")\n";
   for( itemtype item_size = 1; item_size < main_trie.maxpath+1; item_size++ )
   {
      //input_output_manager<< "Frequent " << item_size;
      //input_output_manager << "-itemsets:\nitemset (occurrence)\n";
      set<itemtype> frequent_itemset;
      write_content_to_file_assist( input_output_manager, 
				    &main_trie, item_size, frequent_itemset );
   }
}

void Apriori_Trie::show_content_preorder( ) const
{
   main_trie.show_content_preorder( );
}


Apriori_Trie::~Apriori_Trie()
{
}

/**
  \param maybe_candidate The itemset that has to be checked.
 */

bool Apriori_Trie::is_all_subset_frequent( 
   const set<itemtype>& maybe_candidate ) const
{
   if( maybe_candidate.size() < 3) return true; // because of the 
                                                // candidate generation method!
   else
   {
      set<itemtype>                 temp_itemset(maybe_candidate);
      set<itemtype>::const_iterator item_it = --(--maybe_candidate.end());
      do
      {
         item_it--;
         temp_itemset.erase( *item_it );
         if( !main_trie.is_included( temp_itemset, temp_itemset.begin() ) ) 
	    return false;
         temp_itemset.insert( *item_it );
      }
      while ( item_it != maybe_candidate.begin() );
      return true;
   }
}

void Apriori_Trie::candidate_generation_two()
{
   if( !main_trie.edgevector.empty() )
   {
      main_trie.maxpath = 2;
      temp_counter_array.reserve(main_trie.edgevector.size()-1);
      temp_counter_array.resize(main_trie.edgevector.size()-1);
      for( vector<Edge>::size_type stateIndex = 0; 
	   stateIndex < main_trie.edgevector.size()-1; stateIndex++ )
      {
         temp_counter_array[stateIndex].reserve(
	    main_trie.edgevector.size()-1-stateIndex );
         temp_counter_array[stateIndex].resize(
	    main_trie.edgevector.size()-1-stateIndex, 0);
      }
   }
}

void Apriori_Trie::candidate_generation_assist( 
   Trie* trie, 
   const itemtype distance_from_generator,
   set<itemtype>& maybe_candidate)
{
   itemtype temp_maxpath = trie->maxpath;
   vector<Edge>::iterator itEdge = trie->edgevector.begin();
   if( distance_from_generator )
   {
      for( ; itEdge != trie->edgevector.end(); itEdge++ )
      if( (*itEdge).subtrie->maxpath + 1 >= distance_from_generator )
      {
         maybe_candidate.insert((*itEdge).label);
         candidate_generation_assist(
	    (*itEdge).subtrie, distance_from_generator - 1, maybe_candidate );
         maybe_candidate.erase((*itEdge).label);
	 if( temp_maxpath < (*itEdge).subtrie->maxpath + 1 )
	    temp_maxpath = (*itEdge).subtrie->maxpath + 1;
      }
      if( trie->maxpath < temp_maxpath )
	 trie->maxpath = temp_maxpath;
   }
   else
   {
      vector<Edge>::iterator itEdge2;
      Trie* toExtend;
      for( ; itEdge != trie->edgevector.end(); itEdge++ )
      {
         maybe_candidate.insert((*itEdge).label);
         toExtend = (*itEdge).subtrie;
         for( itEdge2 = itEdge + 1; 
	      itEdge2 != trie->edgevector.end(); itEdge2++ )
         {
            maybe_candidate.insert( (*itEdge2).label );
            if( is_all_subset_frequent( maybe_candidate) )
               toExtend->add_empty_state( (*itEdge2).label );
            maybe_candidate.erase( (*itEdge2).label );
         }
         if( !toExtend->edgevector.empty())
	 {
	    toExtend->maxpath = 1;
	    trie->maxpath=2;	
	 }    
  // we know that state toExtend will not have any more children!
         (vector<Edge>(toExtend->edgevector)).swap(toExtend->edgevector);  
          maybe_candidate.erase((*itEdge).label);
      }

   }
}

/**
     \param basket the given basket
     \param counter The number the processed basket occures 
                    in the transactional database
   */

void Apriori_Trie::find_candidate_two( const vector<itemtype>& basket, 
				       const unsigned long counter )
{
   if( basket.size() > 1)
   {
      vector<itemtype>::const_iterator it1_basket,
                                       it2_basket;

      for( it1_basket = basket.begin(); it1_basket != basket.end()-1; 
	   it1_basket++)
         for( it2_basket = it1_basket+1; it2_basket != basket.end(); 
	      it2_basket++)
            temp_counter_array[*it1_basket][*it2_basket-*it1_basket-1] 
	       += counter;
   }
}

/**
  \param min_occurrence The occurence threshold
*/
void Apriori_Trie::delete_infrequent_two( const double min_occurrence )
{
   vector<Edge>::size_type stateIndex_1,
                            stateIndex_2;
   for( stateIndex_1 = 0; stateIndex_1 < main_trie.edgevector.size()-1; 
	stateIndex_1++ )
   {
      for( stateIndex_2 = 0; 
	   stateIndex_2 < main_trie.edgevector.size() - 1 - stateIndex_1; 
	   stateIndex_2++ )
      {
        if( temp_counter_array[stateIndex_1][stateIndex_2] > min_occurrence )
           main_trie.edgevector[stateIndex_1].subtrie->add_empty_state( 
	      stateIndex_1 + stateIndex_2 + 1,
	      temp_counter_array[stateIndex_1][stateIndex_2] );
      }
      if( !main_trie.edgevector[stateIndex_1].subtrie->edgevector.empty() )
      {
         main_trie.edgevector[stateIndex_1].subtrie->maxpath = 1;
	 main_trie.maxpath = 2;
      }
      temp_counter_array[stateIndex_1].clear();
 /// temp_counter_array[stateIndex_1] will never be used again!
      vector<unsigned long>().swap(temp_counter_array[stateIndex_1]);  
   }
   temp_counter_array.clear();
 /// temp_counter_array will never be used again!
   vector< vector<unsigned long> >().swap(temp_counter_array);
}

void Apriori_Trie::assoc_rule_find( 
   const double min_conf, set<itemtype>& condition_part, 
   set<itemtype>& consequence_part, const unsigned long union_support, 
   Input_Output_Manager& input_output_manager ) const
{
   itemtype item;
   for( set<itemtype>::const_iterator item_it = consequence_part.begin(); 
	item_it != consequence_part.end(); item_it++)
   if( condition_part.empty() || *(--condition_part.end()) < *item_it)
   {
      item = *item_it;
      consequence_part.erase( item );
      condition_part.insert( item );
      if( union_support > main_trie.is_included(
	     condition_part, condition_part.begin() )->counter * min_conf )
      {
	
	if (union_support > 1) {

	        input_output_manager.write_out_basket(condition_part);
        	//input_output_manager<< "==> ";
		//input_output_manager<< " ";
        	input_output_manager.write_out_basket(consequence_part);

		//support of empty set
        	double supp_empty = (double)main_trie.counter;
		//support of A
		double supp_A = main_trie.is_included(condition_part, condition_part.begin())->counter;
		//support of B
		double supp_B = main_trie.is_included(consequence_part, consequence_part.begin())->counter;
		
		double conf = (double)union_support / supp_A;
	
		double p_A = supp_A / supp_empty;
		double p_B = supp_B / supp_empty;
	
		double J;
		if ((conf > 0) && (conf < 1)) {
			J = p_A * (conf*log(conf/p_B) + (1-conf)*log((1-conf) / (1-p_B)));
		} else if (conf == 1) {
			J = p_A *conf*log(conf/p_B);
		} else if (conf == 0) {
			J = (1-conf)*log((1-conf) / (1-p_B));
		}
		//J = sqrt(J);
	
        	 //input_output_manager<< "("<<((double) union_support) 
		  //  / main_trie.is_included(condition_part, 
			//		    condition_part.begin())->counter;
		 //input_output_manager<< ", " << union_support << ", " << J <<')';
		input_output_manager << conf << " " << J << "\n";// << " suppA: " << supp_A << " suppB: " 
						//<< supp_B << " suppEmpt: " << supp_empty
						//<< " suppUnion: " << union_support;
	}
      }
      else if( consequence_part.size() > 1 ) 
	 assoc_rule_find( min_conf, condition_part, 
			  consequence_part, union_support, 
			  input_output_manager );
      
	item_it = (consequence_part.insert( item )).first;
      condition_part.erase( item );
   }
}

void Apriori_Trie::assoc_rule_assist( 
   const double min_conf, const Trie* trie, 
   set<itemtype>& consequence_part, 
   Input_Output_Manager& input_output_manager) const
{
   if( consequence_part.size() > 1 )
   {
      set<itemtype> condition_part;
      assoc_rule_find( min_conf, condition_part, consequence_part, 
		       trie->counter, input_output_manager );
   }
   for( vector<Edge>::const_iterator it_item = trie->edgevector.begin(); 
	it_item != trie->edgevector.end(); it_item++)
   {
      consequence_part.insert( (*it_item).label );
      assoc_rule_assist( min_conf, (*it_item).subtrie, consequence_part, 
			 input_output_manager);
      consequence_part.erase( (*it_item).label );
   }
}


void Apriori_Trie::write_content_to_file_assist( 
   Input_Output_Manager& input_output_manager, const Trie* trie, 
   const itemtype distance_from_frequent, 
   set<itemtype>& frequent_itemset ) const
{
   if( distance_from_frequent )
   {
      for( vector<Edge>::const_iterator it = trie->edgevector.begin(); 
	   it != trie->edgevector.end(); it++ )
      if( (*it).subtrie->maxpath + 1 >= distance_from_frequent )
      {
         frequent_itemset.insert( (*it).label );
         write_content_to_file_assist( input_output_manager, 
				       (*it).subtrie, 
				       distance_from_frequent -1, 
				       frequent_itemset );
         frequent_itemset.erase( (*it).label );
      }
   }
   else 
      input_output_manager.write_out_basket_and_counter( frequent_itemset, 
							 trie->counter );
}

