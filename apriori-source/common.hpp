/***************************************************************************
                          common.hpp  -  description
                             -------------------
    begin                : cs march 14 2004
    copyright            : (C) 2004 by Ferenc Bodon
    email                : bodon@cs.bme.hu
 ***************************************************************************/

#ifndef common_HPP
#define common_HPP

/**
  *@author Ferenc Bodon
  */

  /** The type of the item.
    *
    * Items are represented by non-negative integers. 
    * If we know that no itemcode is larger than \f$2^{16}\f$, we can recomplie
    * the code using unsigned short as itemtype.
    */
typedef unsigned long itemtype;
//typedef unsigned short itemtype;
//typedef long itemtype;

#endif
