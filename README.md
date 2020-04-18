# PyCrypt
An program to encrypt / decrypt files and directories

## How it works
### File encryption
Read a file as binary, encrypt it with a key (the password entered) and then write a file with the encrypted file and the key.

### Folder encryption
Build an index with every files of the folder crypted and the empty directories. Put them with the key in a file.  
For decryption, the folder will be rebuilt according to the index by decrypting each enrty.  

## Is it secure ?
__No__. The key (password) is hashed with SHA256 so it can take some time to find if it is long and complex.  

## Updates
### 18/04/2020
 - disable radiobutton and the pw entry
 - Replace password by stars and show only the letter on the left of the cursor
