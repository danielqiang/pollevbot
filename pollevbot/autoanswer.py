import openai
openai.api_key = API_KEY

def get_answer(question):
	prompt = f"You are QuizGPT, an LLM designed to provide the id of the right answer to quiz questions. You will be provided with a question, and potential answers. Each answer is proceeded by its id, a 9 digit number. For instance, for the line \"123456789: C) test\", the number 123456789 is the id, and the rest is the answer body. Answer the following question by providing only the id of the correct answer. You MUST choose one of the answers included in the prompt. Do not explain your thinking. The question is:\n{question}"

	print(question)

	completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}])
	return completion.choices[0].message.content

if __name__ == "__main__":
	print(get_answer("""Which of these equations is correct?
132375398: A) 2+2=5
132375399: B) 2+2=4"""))
