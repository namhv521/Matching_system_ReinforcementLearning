"""
Hangman is a classic word-guessing game. Its origins are not exactly known but it appears to date back to Victorian times. A player writes down the first and last letters of a word and another player guesses the letters in between.

Program randomly selects a word from a list of secret words.
Player has limited chances to guess the word.
When a correct letter is guessed, it is revealed in its correct position.
Player wins if all letters are guessed before running out of chances.
For simplicity, the program gives word length + 2 chances.
Example: If the secret word is mango (5 letters), the player gets 7 chances.

Steps to Build the Game
Create a list of words and randomly select one.
Display blanks (_) for each letter in the word.
Take a letter as input from the user.
Check whether the letter exists in the word.
Reveal correct letters and track wrong guesses.
Display the Hangman drawing after each incorrect guess.
End the game when the word is guessed or all chances are used.
"""
import random
from collections import Counter

someWords = '''apple banana mango strawberry
orange grape pineapple apricot lemon coconut watermelon 
cherry papaya berry lychee muskmelon'''

someWords = someWords.split(' ')
stages = [
    '''
      -----
      |   |
          |
          |
          |
          |
    ---------
    ''',
    '''
      -----
      |   |
      O   |
          |
          |
          |
    ---------
    ''',
    '''
      -----
      |   |
      O   |
      |   |
          |
          |
    ---------
    ''',
    '''
      -----
      |   |
      O   |
     /|   |
          |
          |
    ---------
    ''',
    '''
      -----
      |   |
      O   |
     /|\\  |
          |
          |
    ---------
    ''',
    '''
      -----
      |   |
      O   |
     /|\\  |
     /    |
          |
    ---------
    ''',
    '''
      -----
      |   |
      O   |
     /|\\  |
     / \\  |
          |
    ---------
    '''
]
word = random.choice(someWords)

if __name__ == '__main__' :
    print('Guess the word! HINT: word is a fruit')
    for _ in word:
        print('_', end=' ')
    print()

    letterGuesses = ''
    wrong_guesses = 0
    max_chances = len(stages) - 1
    flag = 0

    try:
        while wrong_guesses < max_chances and flag == 0:
            print()
            guess = input('Enter a letter to guess: ').lower()

            if not guess.isalpha():
                print("Enter only a letter!")
                continue

            elif len(guess) > 1:
                print("Enter only a single letter")
                continue

            elif guess in letterGuesses:
                print("You already guessed that letter!")
                continue

            if guess in word:
                letterGuesses += guess * word.count(guess)
            else:
                wrong_guesses += 1
                print(stages[wrong_guesses])

            for char in word:
                if char in letterGuesses:
                    print(char, end=' ')
                else:
                    print('_', end=' ')
            if Counter(letterGuesses) == Counter(word):
                print("\nCongratulations! u guessed the word:", word)
                flag = 1
                break
        if wrong_guesses == max_chances:
            print("\nyou lost! the word was:", word)

    except KeyboardInterrupt:
        print('\nGame interrupted. bye!')
