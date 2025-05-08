import json
import re
from difflib import SequenceMatcher

class KomodoTourChatbot:
    """
    A terminal-based chatbot for answering questions about Komodo National Park tours.
    Uses string similarity matching to find the closest question in the dataset.
    """
    
    def __init__(self, qa_data, similarity_threshold=0.75):
        """
        Initialize the chatbot with question-answer data.
        
        Args:
            qa_data (list): List of question-answer dictionaries
            similarity_threshold (float): Minimum similarity score to consider a match
        """
        self.qa_data = qa_data
        self.similarity_threshold = similarity_threshold
    
    def preprocess_text(self, text):
        """
        Clean and normalize text for better matching.
        
        Args:
            text (str): Input text to process
            
        Returns:
            str: Processed text
        """
        # Convert to lowercase
        text = text.lower()
        # Remove punctuation
        text = re.sub(r'[^\w\s]', '', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text
    
    def calculate_similarity(self, text1, text2):
        """
        Calculate similarity between two strings using SequenceMatcher.
        
        Args:
            text1 (str): First string
            text2 (str): Second string
            
        Returns:
            float: Similarity score between 0 and 1
        """
        return SequenceMatcher(None, text1, text2).ratio()
    
    def find_best_match(self, user_question):
        """
        Find the best matching question in the dataset.
        
        Args:
            user_question (str): The question asked by the user
            
        Returns:
            tuple: (best_match_question, best_match_answer, similarity_score)
                  or (None, None, 0) if no match found above threshold
        """
        if not self.qa_data:
            return None, None, 0
        
        # Preprocess the user question
        processed_question = self.preprocess_text(user_question)
        
        best_match = None
        best_score = 0
        best_answer = None
        
        for qa_pair in self.qa_data:
            question = qa_pair["question"]
            processed_stored_question = self.preprocess_text(question)
            
            # Calculate similarity
            similarity = self.calculate_similarity(processed_question, processed_stored_question)
            
            if similarity > best_score:
                best_score = similarity
                best_match = question
                best_answer = qa_pair["answer"]
        
        # Return the best match if above threshold
        if best_score >= self.similarity_threshold:
            return best_match, best_answer, best_score
        else:
            return None, None, best_score
    
    def find_similar_questions(self, user_question, n=5):
        """
        Find the n most similar questions in the dataset.
        
        Args:
            user_question (str): The question asked by the user
            n (int): Number of similar questions to return
            
        Returns:
            list: List of tuples (question, similarity_score) sorted by similarity
        """
        if not self.qa_data:
            return []
        
        # Preprocess the user question
        processed_question = self.preprocess_text(user_question)
        
        # Calculate similarity for all questions
        similarities = []
        for qa_pair in self.qa_data:
            question = qa_pair["question"]
            processed_stored_question = self.preprocess_text(question)
            similarity = self.calculate_similarity(processed_question, processed_stored_question)
            similarities.append((question, similarity))
        
        # Sort by similarity (descending) and return top n
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:n]
    
    def save_qa_data(self, file_path):
        """
        Save the current QA data to a JSON file for easy updates.
        
        Args:
            file_path (str): Path where to save the JSON file
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(self.qa_data, file, indent=4)
            print(f"QA data saved to {file_path}")
        except Exception as e:
            print(f"Error saving QA data: {e}")
    
    def add_qa_pair(self, question, answer):
        """
        Add a new question-answer pair to the dataset.
        
        Args:
            question (str): The new question
            answer (str): The corresponding answer
        """
        self.qa_data.append({"question": question, "answer": answer})
        print("New QA pair added successfully!")
    
    def run(self):
        """
        Run the chatbot in a terminal-based loop.
        """
        print("\nKomodo National Park Tour Guide Chatbot")
        print("======================================")
        print("Hi! How can I help you today?")
        print("(Type 'exit' or 'quit' to end the conversation)")
        
        while True:
            user_input = input("\nYou: ").strip()
            
            # Check if user wants to exit
            if user_input.lower() in ['exit', 'quit', 'bye', 'goodbye']:
                print("Thank you for chatting with us! Have a great day!")
                break
            
            # Find the best match for the user's question
            best_match, answer, similarity = self.find_best_match(user_input)
            
            # If a good match is found, provide the answer
            if best_match and answer:
                print(f"\nChatbot: {answer}")
            else:
                print("\nChatbot: I'm not sure I understand your question. Did you mean one of these?")
                similar_questions = self.find_similar_questions(user_input)
                
                for i, (question, sim) in enumerate(similar_questions, 1):
                    print(f"{i}. {question}")
                
                print("\nPlease try rephrasing your question or select one of the above options (1-5).")
                
                # Allow the user to select from suggestions
                selection = input("Enter a number or ask a new question: ").strip()
                
                if selection.isdigit() and 1 <= int(selection) <= len(similar_questions):
                    selected_idx = int(selection) - 1
                    if selected_idx < len(similar_questions):
                        selected_question = similar_questions[selected_idx][0]
                        
                        # Find the answer for the selected question
                        for qa_pair in self.qa_data:
                            if qa_pair["question"] == selected_question:
                                print(f"\nChatbot: {qa_pair['answer']}")
                                break


def main():
    """Main function to run the Komodo Tour chatbot."""
    
    # The QA data from the provided JSON file
    qa_data = [
        {
            "question": "Do I need to book a guided ticket?",
            "answer": "It is mandatory, because if you do not book a guided ticket you will not be able to track within the Komodo National Park area."
        },
        {
            "question": "Do Nusabadjo tour guides speak English?",
            "answer": "Most of our guides speak good English."
        },
        {
            "question": "Can I book my ticket on the same day?",
            "answer": "Yes, the guide tickets available do not have a booking limit."
        },
        {
            "question": "How old are children required to purchase tickets?",
            "answer": "Children who are 6 years old are required to purchase a ticket."
        },
        {
            "question": "Is there a special price for children?",
            "answer": "There is no special price for children."
        },
        {
            "question": "Can I cancel my booking?",
            "answer": "You cannot cancel a paid ticket booking."
        },
        {
            "question": "Can I change my booking date?",
            "answer": "You can make changes to the departure date up to H-1 before the departure date."
        },
        {
            "question": "What is the limit to change the departure date?",
            "answer": "You can only change the departure date once."
        },
        {
            "question": "Does the guide ticket include entrance ticket to Komodo National Park?",
            "answer": "The guide ticket does not include the entrance ticket to Komodo National Park."
        },
        {
            "question": "What should I bring on the guided tour?",
            "answer": "We recommend that you bring sunblock, a hat, comfortable shoes, drinking water, and weather-appropriate clothing."
        },
        {
            "question": "Can I interact directly with the Komodo dragons?",
            "answer": "Visitors are strictly prohibited from interacting directly with the dragons."
        },
        {
            "question": "Is there a risk of bad weather during the tour?",
            "answer": "We always monitor the weather conditions and will inform you if there are any changes that affect the tour."
        },
        {
            "question": "Do the tour guides carry first aid equipment?",
            "answer": "Yes, our guides are equipped with first aid kits for emergency situations."
        },
        {
            "question": "How to maintain safety while trekking on the island?",
            "answer": "Our guides will provide clear instructions on how to keep safe while trekking on the island, including choosing safe trails and keeping a distance from wild animals."
        },
        {
            "question": "Are tours to Komodo National Park available every day?",
            "answer": "Yes, we provide tours every day, but it is recommended to book in advance, especially in high season."
        },
        {
            "question": "How to reach Komodo National Park from Labuan Bajo?",
            "answer": "You can reach Komodo National Park by boat from Labuan Bajo, which takes about 2-3 hours depending on your destination."
        },
        {
            "question": "Is there a place to camp in Komodo National Park?",
            "answer": "Camping is one of the prohibited activities in Komodo National Park."
        },
        {
            "question": "Is the tour conducted in bad weather?",
            "answer": "Visitor safety is our priority. In case of bad weather, tours may be canceled or rescheduled to maintain safety."
        },
        {
            "question": "Are there any medical facilities around Komodo National Park?",
            "answer": "There are medical facilities within Komodo National Park for first aid, but we strongly recommend that you bring your own medication during the tour."
        },
        {
            "question": "Are the guided tours in Komodo National Park suitable for the elderly?",
            "answer": "We have more relaxed tours for the elderly with shorter routes and lighter activities. Please let the guide know so we can adjust accordingly."
        },
        {
            "question": "What is Nusabadjo doing to support the conservation of Komodo National Park?",
            "answer": "Nusabadjo works closely with local authorities to support conservation programs, including educating visitors about the importance of nature conservation."
        },
        {
            "question": "Can I do other activities besides trekking, such as photography or bird watching?",
            "answer": "Of course, Komodo National Park has a wide variety of flora and fauna suitable for photography and bird watching. Our guides will help you find the best spots."
        }
    ]
    
    # Option to save the data to a JSON file for future use
    # with open('komodo_qa_data.json', 'w', encoding='utf-8') as f:
    #     json.dump(qa_data, f, indent=4)
    
    # Initialize the chatbot with the data
    chatbot = KomodoTourChatbot(qa_data=qa_data, similarity_threshold=0.6)
    
    # Run the chatbot
    chatbot.run()


if __name__ == "__main__":
    main()