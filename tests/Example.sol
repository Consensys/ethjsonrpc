pragma solidity ^0.4.0;

contract Example {

   string s;

   function set_s(string new_s) {
       s = new_s;
   }

   function get_s() returns (string) {
       return s;
   }
}
