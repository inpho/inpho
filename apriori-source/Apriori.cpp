/***************************************************************************
                          apriori.cpp  -  description
                             -------------------
    begin                : cs dec 26 2002
    copyright            : (C) 2002 by Ferenc Bodon
    email                : bodon@mit.bme.hu
 ***************************************************************************/

#include "Apriori.hpp"
#include <iostream>
#include <vector>
#include <set>
#include <cmath>   //because of the ceil function

using namespace std;

/**
  \param candidate_size The size of the candidate whose support 
                        has top be determined.
*/
void Apriori::support( const itemtype& candidate_size )
{
   set<itemtype> basket;
   vector<itemtype> basket_v;
   if( store_input )
   {
      if (candidate_size == 2)
      {
         while( input_output_manager.read_in_a_line( basket ) )
         {
            input_output_manager.basket_recode( basket, basket_v );
            if (basket_v.size()>1) reduced_baskets[basket_v]++;
         }
      }
      for (map<vector<itemtype>,unsigned long>::iterator it = 
	      reduced_baskets.begin(); it!=reduced_baskets.end();it++)
         apriori_trie->find_candidate(it->first,candidate_size,it->second);
   }
   else while( input_output_manager.read_in_a_line( basket ) )
   {
      input_output_manager.basket_recode(basket, basket_v);
          apriori_trie->find_candidate(basket_v,candidate_size);
   }
}
/**
  \param basket_file The file that contain the transactions.
  \param output_file_name The name of file where the results have to be 
                          written to.
  \param store_input If store_input = true, then the filtered baskets 
                     will be stored in memory

*/
Apriori::Apriori( ifstream& basket_file, const char*  output_file_name, 
                  const bool store_input):
                  input_output_manager(basket_file, output_file_name ),
                  store_input(store_input)
{
}

/**
  \param min_supp The relative support threshold
  \param min_conf The confidence threshold for association rules. 
                  If min_conf=0 no association rules will be extraced.
  \param quiet If quiet = true then no system messages will be written 
               during the process.
  \param size_threshold Frequent itemsets above this threshold 
                        do not need to be found.
*/
void Apriori::APRIORI_alg( const double min_supp, const double min_conf, 
			   const bool quiet, 
			   const unsigned long size_threshold )
{
   unsigned long basket_number;   
   if(!quiet) cout<<endl<<"\t\tFinding frequent itemsets..."<<endl<<endl;
   itemtype candidate_size=1;
   itemtype longest_path,longest_path_after_delete=1;
   if(!quiet)
   {
      cout<<endl<<"Determining the support of the items";
      cout<<" and deleting infrequent ones!"<<endl;
   }
   vector<unsigned long> support_of_items;
   basket_number = input_output_manager.find_frequent_items( 
      min_supp, support_of_items );
   apriori_trie = new Apriori_Trie( basket_number );
   apriori_trie->insert_frequent_items( support_of_items );

//   apriori_trie->show_content();
//   getchar();
   double min_supp_abs = min_supp * basket_number;
   longest_path_after_delete = apriori_trie->longest_path();
//   apriori_trie->show_content();
//   getchar();
   longest_path=apriori_trie->longest_path();
   candidate_size++;
   if(!quiet) 
   {
      cout<<endl<<"Genarating "<<candidate_size;
      cout<<"-itemset candidates!"<<endl;
   }
   apriori_trie->candidate_generation(candidate_size-1);
//   apriori_trie->show_content();
//   getchar();
   while( longest_path<apriori_trie->longest_path() )
   {
      input_output_manager.rewind();
      if(!quiet)
      {
	 cout<<"Determining the support of the "<<candidate_size;
	 cout<<"-itemset candidates!"<<endl;
      }
      support( candidate_size );
//      apriori_trie->show_content();
//      getchar();
      if(!quiet) cout<<"Deleting infrequent itemsets!"<<endl;
      apriori_trie->delete_infrequent(min_supp_abs, candidate_size);
      longest_path_after_delete=apriori_trie->longest_path();
//      apriori_trie->show_content();
//      getchar();
      if (candidate_size == size_threshold )
      {
	 if(!quiet) cout<<"Size threshold is reached!"<<endl;
	 break;
      }
      longest_path=apriori_trie->longest_path();
      candidate_size++;
      if( !quiet )
      {
	 cout<<endl<<"Genarating "<<candidate_size;
	 cout<<"-itemset candidates!"<<endl;
      }
      apriori_trie->candidate_generation(candidate_size-1);
//      apriori_trie->show_content_preorder();
//      getchar();
   }
   apriori_trie->write_content_to_file( input_output_manager );
   if (min_conf)
   {
      if(!quiet) cout<<"\nGenerating association rules...!\n";
      apriori_trie->association( min_conf, input_output_manager );
   }
   if(!quiet) cout<<"\nMining is done!\n";
}

Apriori::~Apriori()
{
   delete apriori_trie;
}
