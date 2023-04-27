import streamlit as st
import torch
import numpy as np
import pickle as pkl

# Define your function here


def answer_question(passage, question, tokenizer_for_bert, model, max_len=500):

   input_ids = tokenizer_for_bert.encode(question, passage, max_length=max_len, truncation=True)
   
   sep_index = input_ids.index(102)
   len_question = sep_index + 1
   len_passage = len(input_ids)-len_question
   
   segment_ids = [0]*len_question + [1]*(len_passage)
   
   tokens = tokenizer_for_bert.convert_ids_to_tokens(input_ids)
   
   start_token_scores = model(torch.tensor([input_ids]), token_type_ids=torch.tensor([segment_ids]))[0]
   end_token_scores = model(torch.tensor([input_ids]), token_type_ids=torch.tensor([segment_ids]))[1]
   
   start_token_scores = start_token_scores.detach().numpy().flatten()
   end_token_scores = end_token_scores.detach().numpy().flatten()
   
   answer_start_index = np.argmax(start_token_scores)
   answer_end_index = np.argmax(end_token_scores)
   
   start_token_scores = np.round(start_token_scores[answer_start_index], 2)
   end_token_scores = np.round(end_token_scores[answer_end_index], 2)
   
   answer = tokens[answer_start_index]
   for i in range(answer_start_index + 1, answer_end_index + 1):
    if tokens[i][0:2] == '##':
        answer+=tokens[i][2:]
    else:
        answer+=' '+tokens[i]
  

    if(answer_start_index == 0) or (start_token_scores < 0) or (answer == '[SEP') or (answer_end_index < answer_start_index):
       answer = "Sorry!, I could now find the answer in the passage."
    print("in function",answer)
    return (answer_start_index, answer_end_index, start_token_scores, end_token_scores, answer)

# Set up the Streamlit app
def main():
    st.title("Question Answering App")
    context = st.text_area("Enter the context or passage:")
    question = st.text_input("Enter your question:")
    with open('model.pkl', 'rb') as handle:
        model = pkl.load(handle)
        
    with open('tokenizer.pkl', 'rb') as handle:
        tokenizer_for_bert = pkl.load(handle)

    if st.button("Answer"):
        _, _, _, _, answer = answer_question(context, question, tokenizer_for_bert, model)
        print("out function",answer, '\n')
        answer_display = st.empty()
        answer_display.text_area("Answer:", value=answer, height=10)


if __name__ == "__main__":
    main()
