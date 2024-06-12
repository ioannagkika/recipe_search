from transformers import AutoModelForTokenClassification, AutoTokenizer, pipeline
from pydantic import BaseModel
import torch


# Added this function to reconstrunct the tokens to words
def reconstruct_words_with_metadata(ner_results):
    words_with_metadata = []
    current_word = ''
    current_start = None
    current_certainty_sum = 0
    current_token_count = 0
    current_end = None

    for item in ner_results:
        word = item['word']
        # Merge wordpieces (tokens starting with ##) with the current word
        if word.startswith('##') and item["startPosition"] == current_end:
            current_word += word[2:]  # Remove '##' and append to the current word
        elif word.startswith('##') and item["startPosition"] != current_end:
            continue
        else:
            if current_word:
                # Calculate average certainty
                average_certainty = current_certainty_sum / current_token_count
                # Add the previous word with its metadata to the list
                words_with_metadata.append({
                    "word": current_word,
                    "startPosition": current_start,
                    "endPosition": current_end,
                    "certainty": average_certainty
                })
            # Start a new word
            current_word = word
            current_start = item['startPosition']
            current_certainty_sum = 0
            current_token_count = 0
        current_certainty_sum += item['certainty']
        current_token_count += 1
        current_end = item['endPosition']
    
    if current_word:
        # Calculate average certainty for the last word
        average_certainty = current_certainty_sum / current_token_count
        # Add the last word with its metadata to the list
        words_with_metadata.append({
            "word": current_word,
            "startPosition": current_start,
            "endPosition": current_end,
            "certainty": average_certainty
        })
    
    return words_with_metadata

class NerInput(BaseModel):
    text: str

class Ner:
    model: AutoModelForTokenClassification
    tokenizer: AutoTokenizer
    cuda: bool
    cuda_core: str

    def __init__(self, model_path: str, cuda_support: bool, cuda_core: str):
        self.cuda = cuda_support
        self.cuda_core = cuda_core
        self.model = AutoModelForTokenClassification.from_pretrained(model_path)
        device = -1
        if self.cuda:
            self.model.to(self.cuda_core)
            device = int(cuda_core[5:]) # form is e.g. cuda:3
        self.model.eval() # make sure we're in inference mode, not training

        self.tokenizer = AutoTokenizer.from_pretrained(model_path)

        self.nlp = pipeline("ner", model=self.model, tokenizer=self.tokenizer, device=device)


    async def do(self, input: NerInput):
        text = input.text
        if len(text) == 0:
            return None
        
        ner_results = self.nlp(text)

        '''
        this is how it looks like:
        ner_results = [{
            "entity": "LOC",
            "score": 0.9996141791343689,
            "word": "Berlin",
            "start": 38,
            "end": 44
        }]

        this is how it should look:
        ner_results = [{
            "entity": "LOC",
            "word": "string",
            "certainty": 0.9996141791343689,
            "startPosition": 38,
            "endPosition: 44
        }]
        '''
        
        for item in ner_results:
            # convert numpy.int64 values to native python int values
            item['certainty'] = float(item.pop('score'))
            item['startPosition'] = item.pop('start')
            item['endPosition'] = item.pop('end')
            del item['index']
        
            

        return reconstruct_words_with_metadata(ner_results)
