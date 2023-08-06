#!/usr/bin/env python2.7
__author__ = 'marcsantiago'
from random import choice
from binascii import hexlify, unhexlify
from sys import exit, stdout
from pyminizip import compress
from os import remove
from zipfile import ZipFile
from datetime import datetime

class OneTimePadEncryption:
    """This Class was designed to apply a one time pad encryption
    on textual data that either comes from a file or that is entered
    manually by the user.  Note, the suffix of the key file and the suffix
    of the encrypted message file will be the same.  This allows
    users to associate key files with their corresponding
    encrypted text files"""
    def __init__(self):
        self.my_key = None
        self.my_string = None
        self.string_list = None
        self.key_list = None
        self.file_data = None
        self.timestamp = None

    def __string_converter(self, text_data):
        """Takes a given string or file and converts it to binary"""
        return bin(int(hexlify(text_data), 16))

    def __key_generator(self, standard_string_length):
        """Generates a random list that is equal to
        the length of the provided string."""
        print "Generating Key Please Wait..."
        filename = "_".join(["key", self.timestamp])
        string_length = len(standard_string_length)
        key_list = []
        key_values = range(65, 123)
        for i in xrange(string_length):
            key_list.append(chr(choice(key_values)))

        with open(filename + ".dat", 'w') as data:
            temp_string = ""
            for key in key_list:
                temp_string += key
            data.write(temp_string)
        return self.__string_converter("".join(key_list))
    
    def __password_checker(self, zip_password):
        """checks the password the user entered to zip secure the key.dat file.
        Warns the user if the password is too weak and prompts the user if they
        wish to continue if the password is too weak."""
        cap = 0
        special = 0
        num = 0
        if len(zip_password) < 8:
            print "Warning! The password you have entered is less then 8 character."
            answer = raw_input("do you wish to continue? [y] or [n]\n").lower()
            if answer not in ['y', 'yes']:
                print "Exiting Program..."
                exit(0)
        for ch in zip_password:
            if ch.isdigit():
                num += 1
            elif ch.isupper():
                cap += 1
            elif ch in "!@#$%^&*":
                special += 1
        if num == 0 or cap == 0 or special == 0:
            print "The password you have entered is weak."
            print "A strong password should contain at least one number, one uppercase, and one special character."
            print "Your password contains %d numbers, %d uppercase letters, and %d special characters"\
                  % (num, cap, special)
            answer = raw_input("do you wish to continue? [y] or [n]\n").lower()
            if answer not in ['y', 'yes']:
                print "Exiting Program..."
                exit(0)
            else:
                answer = raw_input("Do you wish to write your zip password to file? [y] or [n]\n").lower()
                if answer in ['y', 'yes']:
                    with open("zip_password.txt", 'w') as data:
                        data.write(zip_password)
                        return zip_password
                else:
                    return zip_password
        else:
            return zip_password
                    
    def __encrypt_file(self, zip_password):
        """Encrypts the key.dat file with a zip encryption using pyminizip.
        For more instructions regarding pyminizip you visit pypi.python.org
        and search for the module."""
        filename = "_".join(["key", self.timestamp])
        compress(filename + ".dat", filename + ".zip", zip_password, int(9))
        remove(filename + ".dat")

    def decrypt_file(self, zip_file, zip_password):
        """Unzips key.zip file using a supplied password"""
        ZipFile(zip_file).extractall(pwd=zip_password)

    def decrypt_string_or_file(self, key, encrypted_string, key_file_mode=False, encrypted_string_file_mode=False):
        """Method that takes either the key or the encrypted string as a
        string or can the key and encrypted string a as file and decrypts
        the string using the provided string. NOTE** In order to use the the key.dat file
        you must first also be able to unzip it using a password."""
        print "Starting Decryption..."
        if key_file_mode is True:
            self.my_key = key
            with open(self.my_key, 'r') as key_data:
                self.my_key = key_data.read()
        else:
            self.my_key = key

        if encrypted_string_file_mode is True:
            self.my_string = encrypted_string
            with open(self.my_string, 'r') as string_data:
                self.my_string = string_data.read()
        else:
            self.my_string = encrypted_string

        my_string_num_list = self.my_string
        my_key_num_list = self.__string_converter(self.my_key)

        decrypt_list = []
        count = 2
        bar_length = 20
        for j in xrange(2, len(my_string_num_list)):
            percent = float(count) / len(my_key_num_list)
            hashes = "#" * int(round(percent * bar_length))
            spaces = " " * (bar_length - len(hashes))
            stdout.write("\rPercent: [{0}] {1}%".format(hashes + spaces, int(round(percent * 100))))
            stdout.flush()
            decrypt_list.append(int(my_string_num_list[j]) ^ int(my_key_num_list[j]))
            count += 1
        print
        decrypt_list = [str(i) for i in decrypt_list]
        add_binary = "0b" + "".join(decrypt_list)
        decrypted_string = int(add_binary, 2)
        message = unhexlify('%x' % decrypted_string)

        with open("decrypted_message.txt", 'w') as out_message:
            out_message.write(str(message))
        print "Decryption Complete."
        return message

    def encrypt_string_or_file(self, plain_text, string_file_mode=False):
        """Method that takes either the key or plaintext as a
        string or file. The key is randomly generated for you!"""
        print "Starting Encryption..."
        self.timestamp = str(datetime.now().strftime("%y%m%d_%H%M%S"))
        filename = "_".join(["encrypted_message", self.timestamp])
        if string_file_mode is True:
            with open(plain_text) as plaintext_data:
                self.file_data = str(plaintext_data.read())
                self.string_list = self.__string_converter(self.file_data)
                self.key_list = self.__key_generator(self.file_data)
        else:
            self.string_list = self.__string_converter(plain_text)
            self.key_list = self.__key_generator(plain_text)

        encrypted_list = []
        count = 2
        bar_length = 20
        for j in xrange(2, len(self.string_list)):
            percent = float(count) / len(self.string_list)
            hashes = "#" * int(round(percent * bar_length))
            spaces = " " * (bar_length - len(hashes))
            stdout.write("\rPercent: [{0}] {1}%".format(hashes + spaces, int(round(percent * 100))))
            stdout.flush()
            encrypted_list.append(int(self.string_list[j]) ^ int(self.key_list[j]))
            count += 1
        print
        encrypted_list = [str(i) for i in encrypted_list]
        encrypted_data = "0b" + "".join(encrypted_list)

        with open(filename + ".txt", 'w') as message:
            message.write(encrypted_data)

        self.__encrypt_file(self.__password_checker(raw_input("Please type in a password to zip "
                                                              "and encrypt the key.dat file\n")))
        print "Encryption Complete."
        return encrypted_data