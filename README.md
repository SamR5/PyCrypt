# PyCrypt
An program to encrypt / decrypt files and directories

## How it works
### File encryption
Read a file as binary, encrypt it with a key (the password entered) and then write a file with the encrypted file and the key.

### Folder encryption
Build an index with every files of the folder crypted and the empty directories. Put them with the key in a file.  
For decryption, the folder will be rebuilt according to the index by decrypting each enrty.  

## Is it secure ?
__No__. The key (password) is hashed with SHA256 so it can take some time to find it if it is long and complex.  

## TODO
 - disable radiobutton and the pw entry
 - Replace password by stars and bind 'Return' to show
 - add compiled C++ functions in cryptutils with ctypes to accelerate
