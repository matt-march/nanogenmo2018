# nanogenmo2018

This project builds 50,000 word novels with a top-down mechanical process described below. My example, "request, anything, and kindness.txt", was built using novels from Project Gutenberg. 

[ParseText.py](ParseText.py) turns blocks of text into word to word edge lists (both forward and backwards), and labels the resulting output with tags to use in MakeStory.py. 

[MakeStory.py](MakeStory.py) generates a story by: 
1. Generating a set of main and secondary characters and a narrator, each with a tag to load sets of word to word edge weights (from ParseText.py) for generating sentences
2. Generating a set of scenes by choosing a pair of characters to interact, with each main character having a scnece with most other main characters (up to twice), and each secondary character having a scene with a third of all main characters
3. Each scene alternates a paragrah from the narrator, then one character then another until a minimum number of words has been reached (50,000 words / number of scenes). 
4. Each paragraph is a set of sentences starting either with a random capitalized word, or a topic chosen from the nouns in the previous paragraph
