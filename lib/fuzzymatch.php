<?php

##  These routines by Uri Nodelman and Colin Allen

##  Top level function for use in various contexts, 
##   e.g. word matching, name matching, title matching

##  (float) fuzzy_match(x,y)
##   compares two strings by fuzzy matching words within the string
##   returns ratio (O-1) of number of matched words in shorter title 
##   vs. number of words in shorter title
##   Suggest using a threshold for 0.5 as criterion for title and name matching
##   note: when x and y are single words, the result is boolean

############################################################################
// Global values
############################################################################
$trace = 0; # set to 1 for following recursion
$debug = 0; # set to 1 for general print statements

$word_edit_threshold_default = 2; # global default controling the max number of permissible edits between two matching words

$stoppers = array("the","and","a","an","as","in","at","to","of","on", "philosophy"); # common words


############################################################################
// Examples for testing/debugging
############################################################################
#$s1 = "The Extended Mind";$s2 = "Extended and Embodied Mind";
#$s1 = "The Extedned Embodied Mind";$s2 = "Extended and Embodied Mind";
#$s1 = "The Extedned Mnid";$s2 = "Extended and Embodied Mind";
#$s1 = "Mind Body Problem";$s2 = "Extended and Embodied Mind";

#$s1="Physical Chemistry";$s2="Physics and Chemistry";
#$s1="Aspects of the Evolution of Peter Abelards Thought on Signification and Predication";$s2="On The Plurality of Worlds";
#$s1="eaxtended";$s2="extaended";
#$s1="extendad";$s2="etxtended";
#$s1="apples";$s2="oranges";
#$s1="apples";$s2="grapefruit";
#$s1="extended";$s2="ex tended";
#$s1="doesn't";$s2="does not";
#$s1="Christopher P. Adams"; $s2="Chris Adams";

#print "Compare '$s1' vs. '$s2' ----> ".fuzzy_match($s1,$s2,2)."\n";



############################################################################
// Functions
############################################################################

function fuzzy_match($str1,$str2,$word_edit_threshold) {
  // returns a composite (product of the ratios) of matched words to length of each string
  // this is the top level function that should be called by other functions
  // if you don't call it with a word edit threshold, it will use the global default
  //    set at the top of the file
  global $trace,$debug,$word_edit_threshold_default;
  if (!isset($word_edit_threshold)) {
  	$word_edit_threshold = $word_edit_threshold_default;
  }
  ## regularize strings, removing stopwords, punctuation, etc.
  $str1 = regularize($str1); $str2 = regularize($str2);

  ## turn both wordstrings into lists
  $str1list = preg_split("/\s+/",$str1); $str2list = preg_split("/\s+/",$str2);

  ## result storage
  $match=0;
  $distance=0;
  
  foreach ($str1list as $str1word) {
    foreach ($str2list as $str2word) {
      $matchresult = fuzzy_word_match($str1word,$str2word,$word_edit_threshold);
      if ($matchresult) {
	++$match;
	$distance += ($matchresult - 1);  # because fuzzy_word_match adds one for the match
	break;
      }
    }
  }
  $base1 = count($str1list);
  $base2 = count($str2list);
  if ($base2<$base1) { 
    $ratioshort = ($match / $base1);
    $ratiolong = ($match / $base2);
  } else {
    $ratioshort = ($match / $base2);
    $ratiolong = ($match / $base1);
  }
  
  $ratioproduct = $ratioshort * $ratiolong; # composite match measure

  if ($debug) {  print "$match $ratioshort $ratiolong (cum. dist. $distance)\n"; print_r($str1list); }
  
  if ($match) {
    return "$ratioproduct,$distance"; 
  } else {
    return "0,0";
  }
}

function regularize($string) {
  // (string) returned without some common words, punctuation, contractions, and possessives
  
  global $debug;
  global $stoppers;  
  foreach ($stoppers as $stop) {
    $string = preg_replace("/\b$stop\b\s*/i", "",$string);
  }
  
  $string = preg_replace("/[!?:,]/","",$string);
  $string = preg_replace("/n\'t\b/i"," not",$string);
  $string = preg_replace("/\'s\b/i","s",$string);
  return $string;
}

function fuzzy_word_match($word1,$word2,$word_edit_threshold) {
  // (boolean) returns 1 if fewer than $word_edit_threshold edits, 0 otherwise
  // wrapper for fuzzy_word_recurse which applies word_edit_threshold
  
  global $debug;
  
  $result = fuzzy_word_recurse($word1, $word2, 0, 0, $word_edit_threshold);
  if ($result <= $word_edit_threshold) {
    if ($debug) { print "   MATCH! ($result)\n"; }
    return $result + 1; # guarantee a non-zero result
  } else {
    if ($debug) { print "  NO match!\n"; }
    return 0;
  }
}

function fuzzy_word_recurse($w1,$w2,$err,$lev,$word_edit_threshold) {
  // (float) returns edit distance between w1 and w2 (Damerau-Levenshtein style)
  // recursion on shorter versions of strings based on character matching at
  // at beginning of strings. Checks for substitations, transpositions, and
  // insertions/deletions
  
  global $trace,$debug;
  $l1 = strlen($w1);
  $l2 = strlen($w2);
  
  if ($trace) { # for following recursion
    for ($i=0;$i<$lev;++$i) { print "   "; }
    print "$lev> Called fuzzword($w1,$w2,$err,$lev): comparing ".substr($w1,0,1).' to '.substr($w2,0,1)."\n";
  }
  
  if ( abs($l1 - $l2) > 2 ) {  # common case is that words are more than 2 letters apart in length
    return abs($l1 - $l2);
    
  } elseif ($l1*$l2 == 0) { # if either length is 0 return total current error + length of remaining string
    return $err+$l1+$l2;
    
  } elseif (substr($w1,0,1) == substr($w2,0,1)) { # first character matches, recurse on rest of string
    return fuzzy_word_recurse(substr($w1,1,$l1-1),substr($w2,1,$l2-1),$err,$lev+1,$word_edit_threshold);
    
  } elseif ($err > $word_edit_threshold) { # anything we do from here will increase the error by one
    
    if ($trace) { # for following recursion
      for ($i=0;$i<$lev;++$i) { print "   "; }
      print "---over word_edit_threshold---\n";
    }
    return ($err+1);
    
  } else { ## up to three branches for the recursion now

    if ($trace) { # for following recursion
      for ($i=0;$i<$lev;++$i) { print "   "; }
      print "   Substitution branch:\n"; # Consider this a substitution error
    }

    $subst_err = fuzzy_word_recurse(substr($w1,1,$l1-1),substr($w2,1,$l2-1),$err+1,$lev+1,$word_edit_threshold);
    $min_err = $subst_err;
    
    if ($l1>1) { # Consider this as an insertion to w1 error
      if ($trace) { # for following recursion
	for ($i=0;$i<$lev;++$i) { print "   "; }
	print "   Insertion to w1 branch:\n";
      }
      $ins_err = fuzzy_word_recurse(substr($w1,1,$l1-1),substr($w2,0,$l2),$err+1,$lev+1,$word_edit_threshold);
      if ($ins_err < $min_err)  { $min_err = $ins_err; }
    }
    
    if ($l2>1) { # Consider this as an insertion to w2 error
      if ($trace) { # for following recursion
	for ($i=0;$i<$lev;++$i) { print "   "; }
	print "   Insertion to w2 branch:\n";
      }
      $ins_err = fuzzy_word_recurse(substr($w1,0,$l1),substr($w2,1,$l2-1),$err+1,$lev+1,$word_edit_threshold);
      if ($ins_err < $min_err) { $min_err = $ins_err; }
      
      if ($l1>1
	  and substr($w1,1,1) == substr($w2,0,1)
	  and substr($w1,0,1) == substr($w2,1,1))
	{ # Consider this as a transposition error
	  
	  if ($trace) { # for following recursion
	    for ($i=0;$i<$lev;++$i) { print "   "; }
	    print "   Transposition branch:\n";
	  }
	  $trans_err = fuzzy_word_recurse(substr($w1,2,$l1-2),substr($w2,2,$l2-2),$err+1,$lev+1,$word_edit_threshold);
	  if ($trans_err < $min_err) { $min_err = $trans_err; }
	}
    }
    
    return $min_err; # maximize chance of matching
  } 
}

?>
