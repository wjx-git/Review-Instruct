import argparse
from utils.prompts import Prompter
from utils.person import Candidate, Chairman, Reviewer
import jsonlines
import json


def read_json(file_path):
    questions = []
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for d in data:
            questions.append(d['instruction'])
        return questions
    
def save_history(history, save_file):
    with jsonlines.open(save_file, 'a') as writer:
        writer.write(history)


def review_instruct(promptor, model_chairman, model_candidate, model_reviewers, question, rounds, save_file):

    history = {
        'question': question,
        'num_rounds': rounds,
        'rounds': [],
    }

    chairman = Chairman(promptor, model_chairman, question)
    candidate = Candidate(promptor, model_candidate)
    reviewers = [Reviewer(promptor, model, question) for model in model_reviewers]
    max_tokens = 4096  # max output tokens
    for _ in range(rounds):
        try:
            ############ Response ############
            candidate.add_history('user', question, action_guide = ['<respond>'])
            response = candidate.get_response(max_tokens = max_tokens)
            candidate.chat_history.pop()
            candidate.add_history('user', question)
            candidate.add_history('assistant', response)
            
            history['rounds'].append([('chairman', question), ('candidate', response)])

            ############ Review ############
            criticizes = []
            for i, reviewer in enumerate(reviewers):
                reviewer.add_history('assistant', question)
                reviewer.add_history('user', response['no_thought'], action_guide = ['<criticize>'])
                criticize = reviewer.get_response(max_tokens = max_tokens)
                reviewer.chat_history.pop()
                reviewer.add_history('user', response['no_thought'])
                criticizes.append(f'Judge {str(i+1)}:' + criticize['no_thought'])

            ############ Ask ############
            chairman.add_history('user', question)
            chairman.add_history('assistant', response['no_thought'])
            chairman.add_history('user', '\n'.join(criticizes), action_guide = ['<raise>'])
            question = candidate.get_response(max_tokens = max_tokens)
            chairman.chat_history.pop()

        except Exception as e:
            raise e
    
    save_history(history, save_file)


def run(promptor, model_chairman, model_candidate, model_reviewers, questions, rounds, save_file):
    '''
    Input:
        promptor: prompt class
        model_chairman, model_candidate: str, model names
        model_reviewers: list, model names
        questions: [dict] list of questions items
        rounds: int
        save_file: str
    Output:
        dataset: [dict] list of data
    '''
    dataset = []

    for i, question in enumerate(questions):
        data = review_instruct(promptor, model_chairman, model_candidate, model_reviewers, question, rounds, save_file)
        dataset.append(data)
        print(f'Question id: {str(i+1)} completed.')
    return dataset


if __name__ == "__main__":
    # read arguments
    parser = argparse.ArgumentParser()

    parser.add_argument("--model_chairman", type=str, default='Qwen/Qwen2-72B-Instruct')
    parser.add_argument("--model_candidate", type=str, default='Qwen/Qwen2-72B-Instruct')
    parser.add_argument("--model_reviewers", type=list, default=['Qwen/Qwen2-72B-Instruct'])
    parser.add_argument("--instruction_file", type=str, default='data/alpaca_data.json', help="seed file")
    parser.add_argument("--rounds", type=int, default=2, help="How many rounds of to run")
    parser.add_argument("--save_file", type=str, default='unspecified')
    parser.add_argument("--language", type=str, default='en')

    args = parser.parse_args()

    
    print('Arguments: ', args)

    promptor = Prompter(args.language)
    questions = read_json(args.instruction_file)   # load questions
    debates = run(
        promptor, 
        args.model_chairman, 
        args.model_candidate, 
        args.model_reviewers, 
        questions, 
        args.rounds, 
        args.save_file
    )

                