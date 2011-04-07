/** \mainpage An efficient implemenation of APRIORI algorithm

This program is a very efficient implementation of APRIORI algorithm
proposed by Rakesh Agrawal and Ramakrishnan Srikant.  APRIORI is the
most basic and well-known algorithm to find frequent itemsets in a
transactional database.

<h2>Frequent Itemset Mining problem</h2> A <i>transactional
database</i> consists of sequence of transaction: \f$T=\langle
t_1,\ldots ,t_n\rangle \f$.  A transaction is a set of items
(\f$t_i\in I\f$).  Transactions are often called <i>baskets</i>,
referring to the primary application domain (i.e. market-basket
analysis).  A set of items is often called <i>itemset</i> by the data
mining community.  The <i>(absolute) support</i> or the
<em>occurrence</em> of \f$X\f$ (denoted by \f$supp(X)\f$) is the
number of transactions that are supersets of \f$X\f$ (i.e. that
<em>contain</em> \f$X\f$).  The <em>realtive support</em> is the
absolute support divided by the number of transactions
(i.e. <i>n</i>).  An itemset is <i>frequent</i> if its support is
greater or equal than a threshold value.

<p>
In the frequent itemset mining problem a transaction database and a relative support threshold (traditionally denoted by <i>min_supp</i>) is given and we have to find all frequent itemsets.
</p>

<h2>Association Rule Mining problem</h2>
This program is also capable of mining association rules.
An association rule is like an implication: \f$X\to Y \f$ means that if itemset <em>X</em> occurs in a transaction, than itemset <em>Y</em> also occurs with high probability.
This probability is given by the <em>confidence</em> of the rule.
It is like an approxiamtion of <em>p(Y|X)</em>, it is the number of transactions that contain both <em>X</em> and <em>Y</em> divided by the number of transaction that contain <em>X</em>, thus \f$conf(X\to Y)=\frac{supp(X\cup Y)}{supp(X)}\f$.
The <em>relative support</em> of the association rule \f$X\to Y \f$ is the support of itemset \f$X \cup Y \f$.
The lift of \f$X\to Y \f$ tries to capture the independence of the antecedent and the consequent of the rule: \f$lift(X\to Y)=\frac{supp(X\cup Y)}{supp(X)supp(Y)}\f$
An association rule is <em>valid</em> if its confidence, support and lift are greater than or equal than corresponding threshold values.

<p>
In the association rule mining problem a transaction database and a relative support threshold (traditionally denoted by <i>min_supp</i>), a confidence threshold (traditionally denoted by <i>min_conf</i>), and a lift threshold is given and we have to find all valid association rules.
</p>
 */

#ifdef HAVE_CONFIG_H
#include <config.h>
#endif

#include <iostream>
#include <fstream>
#include <cstdlib>
#include "Apriori.hpp"
using namespace std;


/// This procedure displays the usage of the program.

void usage()
{
   cerr << "\nUsage: apriori basketfile outcomefile min_supp [min_conf]\n";
   cerr << "\n basketfile\t    file, that contains the baskets of itemcodes";
   cerr << "\n outcomefile\t    file to write the outcome";
   cerr << "\n min_supp\t    support threshold";
   cerr << "\n min_conf\t    confidence threshold";

   cerr << "\n\nFile formats:";
   cerr << "\n\nThe basket file is a plan text file. Each row represents a basket. ";
   cerr << "A basket is a set of items seperated by a nonnumeric character (for example white space, comma, colon, etc.). ";
   cerr << "An item is represented by its code which is an integer number greater than or equal to 0.";
   cerr << "\nFor more options please check the configuration file: .apriori_config.";
   cerr << "\n\nHave a succesful mining ;-)";
   cerr << "\n\n\n\t\t\t\t\tFerenc Bodon\n\n";
}
void process_config_file(bool& quiet, bool& store_input, unsigned long& size_threshold)
{
   ifstream config_file(".apriori_config");
   quiet=false;
   store_input=true;

   if( !config_file ) 
   {
      cerr << "Warning: There is no configuration file (.apriori_config)!\n";
      cerr << "Default values are used!"<<flush;
   }
   else
   {
      char temp_string[256];
      config_file.getline(temp_string, 256);
      config_file.getline(temp_string, 256);
      config_file>>quiet;
      if( config_file.fail() )
      { 
	 cerr<<"\nWarning: Failed to read in quiet value from the configuration file!";
	 cerr<<"\nDefault value (false) is used.";
      }
      config_file.getline(temp_string, 256);
      config_file>>store_input;
      if( config_file.fail() )
      { 
	 cerr<<"\nWarning: Failed to read in store_input value from the configuration file!";
	 cerr<<"\nDefault value (true) is used.";
      }
      config_file.getline(temp_string, 256);
      config_file>>size_threshold;
      if( config_file.fail() )
      { 
	 cerr<<"\nWarning: Failed to read in size_threshold value from the configuration file!";
	 cerr<<"\nDefault value (0) is used.";
      }
      config_file.close();
   }
}

/// This procedure processes the arguments.
int process_arguments( int argc, char *argv[], ifstream& basket_file, 
		       double& min_supp, double& min_conf )
{
   if ( argc < 4 )
   {
     usage();
     cerr<<"\nError! There are 3 mandatory arguments!"<<flush;
     return 1;
   }
   basket_file.open(argv[1]);
   if( !basket_file )
   {
      usage();
      cerr << "\nError! The basket file can not be read!"<< flush;
      return 1;
   }
   
   min_supp = atof(argv[3]);
   if ( min_supp <= 0 || min_supp > 1 )
   {
      usage();
      cerr<<"\nError!\n min_supp should be in the interval (0,1].\n"<<flush;
      return 1;
   }
       
   if ( argc == 5 )
   {
      min_conf = atof(argv[4]);
      if ( min_conf <= 0 || min_conf > 1 )
      {
	 usage();
         cerr << "\nError!\n min_conf should be in the interval (0,1].\n"<<flush;
         return 1;
      }
   }
   else min_conf = 0;
   return 0;
}

int main( int argc, char *argv[] )
{
   double min_supp,
          min_conf;
   bool store_input = true,
              quiet = false;
   unsigned long size_threshold;
   ifstream basket_file;
   
   process_config_file(quiet, store_input, size_threshold);
   if( process_arguments( argc, argv, basket_file, min_supp, min_conf ) ) return 1;
      
   if( !quiet )
   {
      cout << "\n********************************************************************";
      cout << "\n***                                                              ***";
      cout << "\n***                Trie based APRIORI algorithm                  ***";
      cout << "\n***                       version: 2.3.2                         ***";
      cout << "\n***                                                              ***";
      cout << "\n***       Implemented by: Ferenc Bodon (bodon@cs.bme.hu)         ***";
      cout << "\n***                                                              ***";
      cout << "\n********************************************************************\n\n";
   }
  
   Apriori apriori( basket_file, argv[2], store_input );
   apriori.APRIORI_alg( min_supp, min_conf, quiet, size_threshold );
   basket_file.close();
   return 0;
}

