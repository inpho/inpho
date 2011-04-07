/***************************************************************************
                          Input_Output_Manager.hpp  -  description
                             -------------------
    begin                : cs march 10 2004
    copyright            : (C) 2004 by Ferenc Bodon
    email                : bodon@cs.bme.hu
 ***************************************************************************/

#ifndef Input_Output_Manager_HPP
#define Input_Output_Manager_HPP

/**
  *@author Ferenc Bodon
  */

#include "common.hpp"  
#include <fstream>
#include <vector>
#include <set>
using namespace std;


/** This class is responsible for the input, output and recode operations.

   In frequent itemset mining (FIM) algorithms only frequent items 
   are of interest. Hence it is useful to represent frequent items with 
   integers: <em>1, 2, ..., n</em>, where <em>n</em> is the number of 
   frequent items. In the original transactional database, the items are also 
   represented with integers, so we have to assign new integers 
   to the frequent items.
   
*/

class Input_Output_Manager:public ofstream
{
public:

   Input_Output_Manager( ifstream& basket_file,  
			 const char* output_file_name );
   
   /// Reads in one transaction from the basketfile.
   int read_in_a_line( set<itemtype>& basket );

   /// Determines the frequent items, 
   /// fills in the new_code an new_code_inverse vectors
   unsigned long find_frequent_items( 
      const double min_supp, vector<unsigned long>& support_of_items );

   /// Creates an other basket that contains only the frequent items recoded.
   void basket_recode( const set<itemtype>& original_basket, 
		       vector<itemtype>& new_basket );

   /// Writes out an itemset to the output file.
   void write_out_basket( const set<itemtype>& itemset );

   /// Writes out an itemset and its counter to the output file.
   void write_out_basket_and_counter( const set<itemtype>& itemset, 
				      const unsigned long counter );

   ///
   void rewind(); 

   ~Input_Output_Manager( );

private:
/// The file that contain the transactions (i.e baskets).
   ifstream& basket_file;
   
  /** The new codes of the frequent items.
    *
    * if new_code[i] is 0, then i is not frequent, otherwise the
    * new code of item i is new_code[i]-1.
    */
   vector<itemtype> new_code;

  /** The inverse of new_code vector.
    *
    * new_code_inverse[new_code[i]-1]=i if i is a frequent item.
    */
   vector<itemtype> new_code_inverse;
};


#endif
