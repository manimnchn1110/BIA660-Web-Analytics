
# coding: utf-8

# Assignment1 - information_extraction
# - import libraries

# In[1]:


from __future__ import print_function
import re
import spacy
from pyclausie import ClausIE


# - load 'en' and clausie instances
# - load pattern object fun  
#     Compile(pattern, flags=0)  
#     Compile a regular expression pattern, returning a pattern object.

# In[2]:


nlp = spacy.load('en')
cl = ClausIE.get_instance()
re_spaces = re.compile(r'\s+')


# - Person Class

# In[3]:


class Person(object):
    def __init__(self, name, likes=None, not_likes=None, has=None, travels=None, friends=None):
        self.name = name
        self.likes = [] if likes is None else likes
        self.not_likes = [] if not_likes is None else not_likes
        self.has = [] if has is None else has
        self.travels = [] if travels is None else travels
        self.friends = [] if friends is None else friends

    def __repr__(self):
        return self.name
        


# - Pet Class

# In[4]:


class Pet(object):
    def __init__(self, pet_type, name=None, likes=None):
        self.name = name
        self.type = pet_type
        self.likes=[] if likes is None else likes


# - Trip Class

# In[5]:


class Trip(object):
    def __init__(self, destination, time):
        self.name = destination
        self.time = time     


# - Create empty lists to collect persons, pets and trips

# In[6]:


persons = []
pets = []
trips = []


# - Read file function

# In[7]:


def process_data_from_input_file(file_path='./assignment_01.data'):
    with open(file_path) as infile:
        cleaned_lines = [line.strip() for line in infile if not line.startswith(('$$$', '###', '==='))]
    return cleaned_lines


# - Define select_person + add_person function  
#     #If input name is one person's name who is in the persons list, return it.  
#     #If not, add this person to the persons list.

# In[8]:


def select_person(name):
    for person in persons:
        if person.name == name:
            return person


# In[9]:


def add_person(name):
    person = select_person(name)
    if person is None:
        new_person = Person(name)
        persons.append(new_person)
        return new_person
    return person


# - Define function related to pet  
#     #If input name is one pet's name who is in the pets list, return it.  
#     #If not, add this pet to the persons list.  
#     #get the persons has a pet

# In[10]:


def select_pet(name):
    for pet in pets:
        if pet.name == name:
            return pet


# In[11]:


def add_pet(type, name=None):
    pet = None
    if name:
        pet = select_pet(name)
    if pet is None:
        pet = Pet(type, name)
        pets.append(pet)
    return pet


# In[12]:


def get_persons_pet(person_name):
    person = select_person(person_name)
    for pet in person.has:
        if isinstance(pet, Pet):
            return pet


# - Define function related to trip

# In[13]:


def select_trip(desintation,time):
    for trip in trips:
        if trip.name == destination:
            return trip


# In[14]:


def add_trip(destination, time):
    trip = None
    if destination:
        trip = select_trip(destination,time)
    
    if trip is None:
        trip = Trip(destination, time)
        trips.append(trip)
    return trip


# In[15]:


def get_persons_trip(person_name):
    person = select_person(person_name)
    for trip in person.travels:
        if isinstance(trip, Trip):
            return trip


# In[16]:


def get_persons_trips(person_name):
    person = select_person(person_name)
    return person.travels


# - define function related to likes or not_likes

# In[17]:


def get_persons_likes(person_name):
    s_person = select_person(person_name)
    o_persons = s_person.likes
    return o_persons


# In[18]:


def get_persons_not_likes(person_name):
    s_person = select_person(person_name)
    o_persons = s_person.not_likes
    return o_persons


# In[19]:


def get_pets_likes(pet_name):
    s_pet = select_pet(pet_name)
    o_pets = s_pet.likes
    return o_pets


# - Define process_relation_triplet function

# In[20]:


def process_relation_triplet(triples):
    global persons, pets, trips, destination
    persons = []
    pets = []
    trips = []
    for triplet in triples:
        sentence = triplet.subject + ' ' + triplet.predicate + ' ' + triplet.object
        doc = nlp(unicode(sentence))
        
        #1) Who has a <pet_type>? 
        #Type 1
        if triplet.subject.endswith('name') and ('dog' in triplet.subject or 'cat' in triplet.subject):
            obj_span = doc.char_span(sentence.find(triplet.object), len(sentence))
            if obj_span[0].pos_ == 'PROPN':
                name = triplet.object
                subj_start = sentence.find(triplet.subject)
                subj_doc = doc.char_span(subj_start, subj_start + len(triplet.subject))
                s_people = [token.text for token in subj_doc if token.ent_type_ == 'PERSON']
                assert len(s_people) == 1
                add_person(s_people[0])
                s_person = select_person(s_people[0])
                s_pet_type = 'dog' if 'dog' in triplet.subject else 'cat'
                pet = add_pet(s_pet_type, name)
                s_person.has.append(pet)
        #Type 2
        if triplet.predicate.endswith('named') and ('dog' in triplet.subject or 'cat' in triplet.subject):
            obj_span = doc.char_span(sentence.find(triplet.object), len(sentence))
            if obj_span[0].pos_ == 'PROPN':
                name = triplet.object
                relate_triplets = []
                s_people = []
                for i in triples:
                    if i.index == triplet.index:
                        relate_triplets.append(i)
                for j in relate_triplets:
                    sentence = j.subject + ' ' + j.predicate + ' ' + j.object
                    doc = nlp(unicode(sentence))
                    subj_start = sentence.find(j.subject)
                    subj_doc = doc.char_span(subj_start, subj_start + len(j.subject))
                    for token in subj_doc:
                        if token.ent_type_ == 'PERSON':
                            s_people= [token.text]
                assert len(s_people) == 1
                add_person(str(s_people[0]))
                s_person = select_person(s_people[0])
                s_pet_type = 'dog' if 'dog' in triplet.subject else 'cat'
                pet = add_pet(s_pet_type, name)
                s_person.has.append(pet)
        #2) Who is [going to|flying to|traveling to|visiting] <place>?
        #Type 1
        if 'trip' in triplet.object:
            time = []
            destination = None
            for t in doc:
                if t.pos_ == 'PROPN' and t.head.text == 'to' :
                    destination = t
                if t.ent_type_ == 'DATE':
                    time.append(str(t))
            time = [' '.join(time)]
            if time != ['']:
                travel = add_trip(destination, time[0])
            subj_start = sentence.find(triplet.subject)
            subj_doc = doc.char_span(subj_start, subj_start + len(triplet.subject))
            s_people = [token.text for token in subj_doc if token.ent_type_ == 'PERSON']
            for i in s_people:
                add_person(i)
                s_person = select_person(i)
                if travel not in s_person.travels:
                    s_person.travels.append(travel)
        #Type 2
        if 'is flying' in triplet.predicate:
            time = []
            destination = None
            for t in doc:
                if t.pos_ == 'PROPN' and t.head.text == 'to' :
                    destination = t
                if t.ent_type_ == 'DATE':
                    time.append(str(t))
            time = [' '.join(time)]
            if time != ['']:
                travel = add_trip(destination, time[0])
            s_person = triplet.subject
            add_person(s_person)
            s_person = select_person(s_person)
            if travel not in s_person.travels:
                s_person.travels.append(travel)

        #Type 3
        if 'leaves' in triplet.predicate:
            time = []
            destination = None
            for t in doc:
                if t.pos_ == 'PROPN' and t.head.text == 'for' :
                    destination = t
                if t.ent_type_ == 'DATE':
                    time.append(str(t))
            time = [' '.join(time)]
            if time != ['']:
                travel = add_trip(destination, time[0])  
            s_person = triplet.subject
            add_person(s_person)
            s_person = select_person(s_person)
            if travel not in s_person.travels:
                s_person.travels.append(travel)
        #Type 4
        if 'is going' in triplet.predicate:
            for t in doc:
                if t.pos_ == 'PROPN' and t.head.text == 'to' :
                    destination = t
                if t.ent_type_ == 'DATE':
                        time.append(str(t))
            time = [''.join(time)]
            if time != ['']:
                travel = add_trip(destination, time[0])  
            s_person = triplet.subject
            add_person(s_person)
            s_person = select_person(s_person)
            if travel not in s_person.travels:
                s_person.travels.append(travel)

        #3) Does person like person?
        for t in doc:
            if t.pos_ == 'VERB' and t.head == t:
                verb = t   
        #doesn't like
        if "does n't like" in triplet.predicate:
            s = add_person(triplet.subject)
            o = add_person(triplet.object)
            if o not in s.not_likes:
                s.not_likes.append(o)
        #like
        elif verb.lemma_ == 'like':
            s = add_person(triplet.subject)
            o = add_person(triplet.object)
            if o not in s.likes:
                s.likes.append(o)  

        #P be friends with P
        if verb.lemma_ == 'be' and triplet.object.startswith('friends with'):
            fw_doc = nlp(unicode(triplet.object))
            with_token = [t for t in fw_doc if t.text == 'with'][0]
            fw_who = [t for t in with_token.children if t.dep_ == 'pobj'][0].text
            if triplet.subject in [e.text for e in doc.ents if e.label_ == 'PERSON'] and fw_who in [e.text for e in doc.ents if e.label_ == 'PERSON']:
                s = add_person(triplet.subject)
                o = add_person(fw_who)
                if o not in s.likes:
                    s.likes.append(o)
                if s not in o.likes:
                    o.likes.append(s)
        #P and P are friends
        if verb.lemma_ == 'be' and triplet.object == 'friends' and 'and' in triplet.subject:
            s_o = []
            fw_doc = nlp(unicode(triplet.subject))            
            for t in fw_doc:
                if t.pos_ == 'PROPN' and t.ent_type_ == 'PERSON':
                    t = add_person(t.text)
                    s_o.append(t)
            if s_o[1] not in s_o[0].likes:
                s_o[0].likes.append(s_o[1])
            if s_o[0] not in s_o[1].likes:
                s_o[1].likes.append(s_o[0])
        #P is friends with P, P and P
        if verb.lemma_ == 'be' and triplet.object.startswith('friends') and 'and' in triplet.object:
            s_o = []
            fw_doc = nlp(unicode(triplet.object))
            for t in fw_doc:
                if t.pos_ == 'PROPN' and t.ent_type_ == 'PERSON':
                    t = add_person(t.text)
                    s_o.append(t)
            s = add_person(triplet.subject)
            if s_o[0] not in s.likes:
                s.likes.append(s_o[0])
            if s_o[1] not in s.likes:
                s.likes.append(s_o[1])
            if s_o[2] not in s.likes:
                s.likes.append(s_o[2])
            if s not in s_o[0].likes:
                s_o[0].likes.append(s)
            if s not in s_o[1].likes:
                s_o[1].likes.append(s)
            if s not in s_o[2].likes:
                s_o[2].likes.append(s)
                


# - Define function related to question  
#     #remove a, an, the  
#     #question who, what

# In[21]:


def preprocess_question(question):
    q_words = question.split(' ')
    for article in ('a', 'an', 'the'):
        try:
            q_words.remove(article)
        except:
            pass
    return re.sub(re_spaces, ' ', ' '.join(q_words))


# In[22]:


def has_question_word(string):
    # note: there are other question words
    for qword in ('who', 'what'):
        if qword in string.lower():
            return True

    return False


# In[23]:


def answer_question(question):
    question_triplet = cl.extract_triples([preprocess_question(question)])[0]
    answers = []
    o_person = None
    # (WHO, has, dog)
    if question_triplet.subject.lower() == 'who' and question_triplet.object == 'dog':
        answer = '{} has a {} named {}.'
        for person in persons:
            pet = get_persons_pet(person.name)
            if pet and pet.type == 'dog':
                answers.append(answer.format(person.name, 'dog', pet.name))
    # (WHO, has, cat)
    elif question_triplet.subject.lower() == 'who' and question_triplet.object == 'cat':
        answer = '{} has a {} named {}.'
        for person in persons:
            pet = get_persons_pet(person.name)
            if pet and pet.type == 'cat':
                answers.append(answer.format(person.name, 'cat', pet.name))
                
    # (WHO, travel, place)
    elif (question_triplet.subject.lower() == 'who') and (question_triplet.predicate == 'is going' or
                                                            question_triplet.predicate == 'is flying' or
                                                            question_triplet.predicate =='is traveling'): 
        if question_triplet.object.lower() == 'to france':
            answer = '{} has a trip to France in {}.'
            for person in persons:
                trip = get_persons_trip(person.name)
                if trip and trip.name.text.lower() == 'france':
                    answers.append(answer.format(person.name, trip.time))
                        
        elif question_triplet.object.lower() == 'to japan':
            answer = '{} has a trip to Japan {}.'
            for person in persons:
                trip = get_persons_trip(person.name)
                if trip and trip.name.text.lower() == 'japan':
                    answers.append(answer.format(person.name, trip.time))
                        
                  
        elif question_triplet.object.lower() == 'to peru':
            answer = '{} has a trip to Peru on {}.'
            for person in persons:
                trip = get_persons_trip(person.name)
                if trip and trip.name.text.lower() == 'peru':
                    answers.append(answer.format(person.name, trip.time))
                        
                  
        elif question_triplet.object.lower() == 'to mexico':
            answer = '{} has a trip to Mexico in {}.'
            for person in persons:
                trips = get_persons_trips(person.name)
                for trip in trips:
                    if trip.name.text.lower() == 'mexico':
                        answers.append(answer.format(person.name, trip.time))                
        else:
            answers.append("I don't know.")
            
    elif ('when' in question_triplet.object.lower()) and (question_triplet.predicate == 'is going' or
                                                        question_triplet.predicate == 'is flying' or
                                                        question_triplet.predicate =='is traveling'): 
        if 'to france' in question_triplet.object.lower() and select_person(question_triplet.subject) in persons:
            answer = '{} has a trip to France in {}.'
            for person in persons:
                trips = get_persons_trips(person.name)
                for trip in trips:
                    if trip.name.text.lower() == 'france' and person.name == question_triplet.subject:
                        answers.append(answer.format(person.name, trip.time)) 
        elif 'to japan' in question_triplet.object.lower() and select_person(question_triplet.subject) in persons:
            answer = '{} has a trip to Japan {}.'
            for person in persons:
                trips = get_persons_trips(person.name)
                for trip in trips:
                    if trip.name.text.lower() == 'japan' and person.name == question_triplet.subject:
                        answers.append(answer.format(person.name, trip.time)) 
        elif 'to peru' in question_triplet.object.lower() and select_person(question_triplet.subject) in persons:
            answer = '{} has a trip to Peru on {}.'
            for person in persons:
                trips = get_persons_trips(person.name)
                for trip in trips:
                    if trip.name.text.lower() == 'peru' and person.name == question_triplet.subject:
                        answers.append(answer.format(person.name, trip.time)) 
        elif 'to mexico' in question_triplet.object.lower() and select_person(question_triplet.subject) in persons:
            answer = '{} has a trip to Mexico in {}.'
            for person in persons:
                trips = get_persons_trips(person.name)
                for trip in trips:
                    if trip.name.text.lower() == 'mexico' and person.name == question_triplet.subject:
                        answers.append(answer.format(person.name, trip.time)) 
        else:
            answers.append("I don't know.")
    
    #(who, like, p)
    elif question_triplet.subject.lower() == 'who' and question_triplet.predicate.lower() == 'likes':
        o_person = select_person(question_triplet.object)
        answer = '{} like {}.'
        for person in persons:
            if o_person in person.likes:
                answers.append(answer.format(person,o_person))
    # (WHO, does P, like)
    elif question_triplet.object.lower() == 'who' and question_triplet.predicate.lower() == 'does like':
        s_person = select_person(question_triplet.subject)
        answer = '{} like {}.'
        for person in persons:
            if person in s_person.likes:
                answers.append(answer.format(s_person, person))
                
    #(DOES, P, like, P)
    elif (question_triplet.subject.startswith('Does') or question_triplet[0].subject.startswith('does')) and question_triplet.predicate == 'like':
            sentence = question_triplet.subject + ' ' + question_triplet.predicate + ' ' + question_triplet.object
            doc = nlp(unicode(sentence))
            for t in doc:
                #print(t.text, t.pos_, t.head, t.ent_type_)
                if t.pos_ == 'PROPN' and (t.text in question_triplet.subject):
                    s_person = select_person(t.text)
                if t.pos_ == 'PROPN' and (t.text in question_triplet.object):
                    o_person = select_person(t.text)
            like_persons = get_persons_likes(s_person.name)
            not_like_persons = get_persons_not_likes(s_person.name)
            if o_person in like_persons:
                answer = "Yes, {} likes {}."
                answers.append(answer.format(s_person.name, o_person.name))
            elif o_person in not_like_persons:
                answer = "No, {} doesn't like {}."
                answers.append(answer.format(s_person.name, o_person.name))

            else:
                answers.append("I don't know.")

                    
    else:
        answers.append("I don't know.")
        
    for answer in answers:
        print(answer)


# In[24]:


def main():
    sents = process_data_from_input_file()
    cl = ClausIE.get_instance()
    triples = cl.extract_triples(sents)
    process_relation_triplet(triples)
        
    question = ' '
    while question[-1] != '?':
        question = raw_input("Please enter your question: ")
        if question[-1] != '?':
            print('This is not a question... please try again')
    
    answer_question(question)
    


# In[25]:


if __name__ == '__main__':
    main()

