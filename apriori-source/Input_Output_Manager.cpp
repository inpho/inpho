/***************************************************************************
                          Input_Output_Manager.cpp  -  description
                             -------------------
    begin                : cs march 10 2004
    copyright            : (C) 2004 by Ferenc Bodon
    email                : bodon@cs.bme.hu
 ***************************************************************************/


/**
  *@author Ferenc Bodon
  */
  
#include "Input_Output_Manager.hpp"
#include <algorithm>

Input_Output_Manager::Input_Output_Manager( ifstream& basket_file, 
					    const char* output_file_name ):
   ofstream(output_file_name), basket_file(basket_file)
{
}

/**
  \param basket The basket that will be filled with the next row of the file.
  \return 0 if the end of file is reached, otherwise 1;
*/
int Input_Output_Manager::read_in_a_line( set<itemtype>& basket )
{
   if( basket_file.eof() ) return 0;
   char          c;
   itemtype      pos;

   basket.clear();
   do
   {
      int item = 0;
      pos = 0;
      basket_file.get(c);
      while(basket_file.good() && (c >= '0') && (c <= '9'))
      {
         item *= 10;
         item += int(c)-int('0');
         basket_file.get(c);
         pos++;
      }
      if( pos ) basket.insert( (itemtype) item );
   }
   while( !basket_file.eof() && c != '\n' );
   return 1;
}

/**
  \param min_supp The (relative) support threshold.
  \param support_of_items The support of the items. 
                          The i<sup>th</sup> least frequent item's support is 
			  given by support_of_items[i].
  \return The number of transactions that the basketfile contains.
*/
unsigned long Input_Output_Manager::find_frequent_items( 
   const double min_supp, vector<unsigned long>& support_of_items )
{
   unsigned long basket_number = 0;
   set<itemtype> basket;
   vector< unsigned long > temp_counter_vector;

   /// Determining the support of the items
   set<itemtype>::iterator it_basket;
   while( read_in_a_line( basket ) )
   {      
      if( !basket.empty() )
      {
         basket_number++;
         for( it_basket = basket.begin(); it_basket != basket.end(); 
	      it_basket++ )
         {
            if( *it_basket + 1  > temp_counter_vector.size() )
	       temp_counter_vector.resize( *it_basket + 1, 0 );
            temp_counter_vector[*it_basket]++;
         }
      }
   }

   /// Finding the frequent items
   double long min_occurrence = min_supp * (basket_number - 0.5);
   vector<unsigned long>::size_type edgeIndex;

   set< pair<unsigned long, itemtype> > temp_set;
   for( itemtype edgeIndex = 0; edgeIndex < temp_counter_vector.size(); 
	edgeIndex++ )
      if( temp_counter_vector[edgeIndex] > min_occurrence )
	 temp_set.insert(
	    pair<unsigned long, itemtype>(temp_counter_vector[edgeIndex],
					  edgeIndex));

   new_code_inverse.clear();
   support_of_items.clear();
   for(set< pair<unsigned long, itemtype> >::iterator it = temp_set.begin();
       it != temp_set.end(); it++)
   {
	 new_code_inverse.push_back((*it).second);
	 support_of_items.push_back((*it).first);
   }
//   reverse( new_code_inverse.begin(),new_code_inverse.end() );
//   reverse( support_of_items.begin(), support_of_items.end() );
   vector<itemtype>(new_code_inverse).swap(new_code_inverse);
   vector<unsigned long >(support_of_items).swap(support_of_items);

   new_code.reserve(  temp_counter_vector.size() + 1 );
   new_code.resize(  temp_counter_vector.size() + 1, 0 );
   for( edgeIndex = 0; edgeIndex < new_code_inverse.size(); edgeIndex++ )
      new_code[new_code_inverse[edgeIndex]] = edgeIndex+1;
   return basket_number;
}
/**
  \param original_basket The basket to filter and recode.
  \param new_basket The created reduced basket
*/
void Input_Output_Manager::basket_recode( 
   const set<itemtype>& original_basket, vector<itemtype>& new_basket )
{
   new_basket.clear();
   for( set<itemtype>::iterator it_basket = original_basket.begin(); 
	it_basket != original_basket.end(); it_basket++ )
     if( new_code[*it_basket] ) new_basket.push_back( new_code[*it_basket]-1 );
   sort( new_basket.begin(), new_basket.end() );     
}

void Input_Output_Manager::write_out_basket(const set<itemtype>& basket)
{
   for( set<itemtype>::const_iterator it_item = basket.begin(); 
	it_item != basket.end(); it_item++)
   {
      operator<<( new_code_inverse[*it_item] );
      put(' ');
   }
}

void Input_Output_Manager::write_out_basket_and_counter(
   const set<itemtype>& itemset, const unsigned long counter)
{
   for( set<itemtype>::const_iterator it_item = itemset.begin(); 
	it_item != itemset.end(); it_item++)
   {
      //operator<<( new_code_inverse[*it_item] );
      //put(' ');
   }
	
	//put('(');
	//operator<<(counter);
	//write(")\n",2);
	//write ("\n", 1);
}

void Input_Output_Manager::rewind()
{
   basket_file.clear();
   basket_file.seekg(0, ios::beg);
}

Input_Output_Manager::~Input_Output_Manager()
{
   close();
}
