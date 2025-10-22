from fastapi import FastAPI, status, Depends, HTTPException
from str_analyzer import schemas, utils, models
from str_analyzer.database import engine, SessionLocal
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session
import json
from datetime import datetime


app = FastAPI()

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post('/strings', status_code=status.HTTP_201_CREATED)
def create_string(request: schemas.String, db: Session = Depends(get_db)):
    value_lower = request.value.lower()
    query_hash = db.query(models.String).filter(
        models.String.value == value_lower).first()

    if value_lower == '':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid request body: Missing 'value' field")

    elif value_lower.isdigit():
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                            detail='Invalid data type: "value" must be a string')

    else:
        if query_hash is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f'String with value {request.value} already exists.')
            # return {'details': f'String with value {request.value} already exists.'}

        else:
            length = len(request.value)
            is_palindrome = utils.single_string_palindrome_checker(value_lower)
            unique_char_count = len(set(request.value))
            word_count = len(request.value.split())
            string_hash = utils.hash_string_sha256(request.value)
            character_freq_map = {char: request.value.count(
                char) for char in set(request.value)}

            new_string = models.String(
                value=value_lower,
                length=length,
                is_palindrome=is_palindrome,
                unique_characters=unique_char_count,
                word_count=word_count,
                sha256_hash=string_hash,
                character_freq=json.dumps(character_freq_map)
            )

            db.add(new_string)
            db.commit()
            db.refresh(new_string)

            return {'id': string_hash,
                    'value': f'{request.value}',
                    'properties': {
                        'length': length,
                        'is_palindrome': is_palindrome,
                        'unique_characters': unique_char_count,
                        'word_count': word_count,
                        'sha256_hash': string_hash,
                        'character_frequency_map': character_freq_map
                    },
                    'created_at': datetime.utcnow()
                    }


@app.get('/strings', status_code=status.HTTP_200_OK)
def string_filtering(is_palindrome, min_length, max_length, word_count, contains_character, db: Session = Depends(get_db)):
   
    if not(min_length.isdigit()) or not(max_length.isdigit()) or not(word_count.isdigit()) or contains_character.isdigit():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Invalid query parameter values or types')
    
    elif type(is_palindrome) == str:
        if is_palindrome.lower() =='true':
            is_palindrome = True
        
        elif is_palindrome.lower() == 'false':
            is_palindrome = False
        
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Invalid query parameter values or types')
    
    min_length = int(min_length)
    max_length = int(max_length)
    word_count = int(word_count)
    contains_character = str(contains_character)

    strings = db.query(models.String).filter(and_(models.String.is_palindrome == is_palindrome,
                                                  models.String.length >= min_length,
                                                  models.String.length <= max_length,
                                                  models.String.word_count == word_count,
                                                  models.String.value.contains(
                                                      contains_character)
                                                  )).all()
    final_result_list = []
    for string in strings:
        final_result_list.append(
            {'id': string.sha256_hash,
             'value': string.value,
             'properties': {
                 'length': string.length,
                 'is_palindrome': string.is_palindrome,
                 'unique_characters': string.unique_characters,
                 'word_count': string.word_count,
                 'sha256_hash': string.sha256_hash,
                 'character_frequency_map': json.loads(string.character_freq)
             },
                'created_at': string.created_at
             })

    return {'data': final_result_list,
            'count': len(final_result_list),
            'filters_applied': {
                'is_palindrome': is_palindrome,
                'min_length': min_length,
                'max_length': max_length,
                'word_count': word_count,
                'contains_character': contains_character
            }
            }


@app.get('/strings/filter-by-natural-language', status_code=status.HTTP_200_OK)
def natural_language(query, db: Session = Depends(get_db)):

    if query.isdigit():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Unable to parse natural language query')
    elif not(query):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Missing 'query' parameter")

    query_lower = query.lower().strip()


    matching_strings = {
        'all single word palindromic strings': {'word_count': 1, 'is_palindrome': True},
        'strings longer than 10 characters': {'min_length': 11},
        'palindromic strings that contain the first vowel': {'is_palindrome': True, 'contains_character': 'a'},
        'strings containing the letter z': {'contains_character': 'z'}
    }

    if query_lower in matching_strings.keys():
        query_filters = matching_strings[query_lower]

        if query_lower == 'all single word palindromic strings':
            word_count = query_filters['word_count']
            is_palindrome = query_filters['is_palindrome']
            strings = db.query(models.String).filter(and_(models.String.is_palindrome == is_palindrome,
                                                          models.String.word_count == word_count,
                                                          )).all()
        elif query_lower == 'strings longer than 10 characters':
            min_length = query_filters['min_length']
            strings = db.query(models.String).filter(
                and_(models.String.length >= min_length)).all()

        elif query_lower == 'palindromic strings that contain the first vowel':
            is_palindrome = query_filters['is_palindrome']
            contains_character = query_filters['contains_character']
            strings = db.query(models.String).filter(and_(models.String.is_palindrome == is_palindrome,
                                                          models.String.value.contains(
                                                              contains_character)
                                                          )).all()

        elif query_lower == 'strings containing the letter z':
            contains_character = query_filters['contains_character']
            strings = db.query(models.String).filter(
                and_(models.String.value.contains(contains_character))).all()

        final_result_list = []
        for string in strings:
            final_result_list.append(
                {'id': string.sha256_hash,
                 'value': string.value,
                 'properties': {
                     'length': string.length,
                     'is_palindrome': string.is_palindrome,
                     'unique_characters': string.unique_characters,
                     'word_count': string.word_count,
                     'sha256_hash': string.sha256_hash,
                     'character_frequency_map': json.loads(string.character_freq)
                 },
                    'created_at': string.created_at
                 })

        return {'data': final_result_list,
                'count': len(final_result_list),
                'interpreted_query':{
                'original': query,
                'parsed_filters': query_filters}
                }

    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Unable to parse natural language query')


"""
Any url path which has dynamic routing should be placed under here
"""


@app.get('/strings/{string_value}', status_code=status.HTTP_200_OK)
def specific_string(string_value, db: Session = Depends(get_db)):
    string = db.query(models.String).filter(
        models.String.value == string_value.lower()).first()
    if not string:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'String does not exist in the system.')

    else:
        return {'id': string.sha256_hash,
                'value': string.value,
                'properties': {
                    'length': string.length,
                    'is_palindrome': string.is_palindrome,
                    'unique_characters': string.unique_characters,
                    'word_count': string.word_count,
                    'sha256_hash': string.sha256_hash,
                    'character_frequency_map': json.loads(string.character_freq)
                },
                'created_at': string.created_at
                }


@app.delete('/strings/{string_value}', status_code=status.HTTP_204_NO_CONTENT)
def delete_string(string_value, db: Session = Depends(get_db)):
    string = db.query(models.String).filter(
        models.String.value == string_value).first()
    print(string)
    if string is not None:
        delete_string = db.query(models.String).filter(
            models.String.value == string_value).delete(synchronize_session=False)
        db.commit()
        return None
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='String does not exist in system')
