from flask import Flask, render_template, request, session, redirect
from nltk.tokenize import RegexpTokenizer
# from gensim.models import KeyedVectors
from nltk.stem import PorterStemmer
from itertools import chain
import pandas as pd
import numpy as np
import pickle
import random
import os


app = application = Flask(__name__)
app.secret_key = "abcd"

# =========================================General Functions Start=================================================================

# The function is used to read the job advertisements from different folders and store the information.
# The information will be stored in the form of an object.
# Sample object returned is as below:
# {
# 'Accounting_Finance': [{'image': 'Job_12345.jpg', 'id': '12345', 'link': <ad_link>, 'company': <company>, 'title': <title>..... }]
# }
# The function can also handle nnewly added jobs
def get_job_ads_object():
    job_ads_dict = {}

    folders = [
        'Accounting_Finance',
        'Engineering',
        'Healthcare_Nursing',
        'Hospitality_Catering',
        'IT',
        'PR_Advertising_Marketing',
        'Sales',
        'Teaching'
    ]

    # Looping through the different folders.
    for folder in folders:
        job_ads_dict.update({folder: []})
        # Looping through each file
        for file in os.listdir(f'data/{folder}'):
            # Opening the file for reading the data
            with open(f'data/{folder}/{file}') as data:
                lines = data.read().splitlines()
                title = [title.lstrip('Title:').strip() for title in lines if title.startswith('Title:')][0]
                company = [company.lstrip('Company:').strip() for company in lines if company.startswith('Company:')]
                content = [content.lstrip('Description:').strip() for content in lines if content.startswith('Description:')][0]
                salary = [salary.lstrip('Salary:').strip() for salary in lines if salary.startswith('Salary:')]
            # Creating the job objects and adding to the corresponding folder.
            job_ads_dict[folder].append({
                'image': f"{file.rstrip('.txt')}.jpg",
                'id': f"{file.rstrip('.txt')[-5:]}",
                'link': f"/{folder}/{file.rstrip('.txt')}",
                'company': company[0] if len(company) else 'Not Specified',
                'title': title,
                'content': f"{content[0:400]}.....",
                'full_content': content,
                'salary': salary[0] if len(salary) else 'Not Specified'
            })
    return job_ads_dict

# The function will return a boolean value, if logged in True else False
def login_or_logout():
    login = False
    if 'username' in session:
        login = True
    return login

# This is used for the tokenization of the data passed.
# The method also converts the tokens into lower cases.
def tokenize(data):
    # Pattern for tokenising
    pattern = r'''(?x)          # set flag to allow verbose regexps
        (?:[A-Za-z]+\.)+        # abbreviations, e.g. U.S.A.
      | \w*[\$£]?(?:\d+,?)+(?:\.\d+)?%?\w*  # currency and percentages, e.g. $12.40, 82%
      | [A-Za-z]+(?:[-'][A-Za-z]*)?       # words with optional internal hyphens and apostrophes
    '''
    # Creating the tokenizer
    tokenizer = RegexpTokenizer(pattern)

    tokenised_data = tokenizer.tokenize(data)
    tokenised_data = [token.lower() for token in tokenised_data]

    return tokenised_data

# This method is used for generating the vector representations of the documents.
def gen_docVecs(wv, tk_txts):
    docs_vectors = []  # initialise document embeddings dictionary list
    for i in range(0, len(tk_txts)):  # Loopint thorugh tokenised descriptions
        tokens = tk_txts[i]
        # Temporary object holding the word embeddings
        temp = {x: [] for x in range(wv.vector_size)}
        for w_ind in range(0, len(tokens)):
            try:
                word = tokens[w_ind]
                word_vec = wv[word]  # Getting the word vector for the token
                for j in range(0, len(word_vec)):
                    # Updating the temporary object
                    temp[j].append(word_vec[j])
            except:  # if the word is unable to be found in the embeddings instead of throwing error we are catching it in the except
                pass
        # Updating the document embedding dictionary list by summing up values of the temporary object
        docs_vectors.append({key: sum(temp[key]) for key in temp.keys()})
    # Returing the data frame of document embeddings
    return pd.DataFrame(docs_vectors)

# ===============================================General Functions End==================================================================

# ===============================================Route Definitions Start================================================================

@app.route('/')
def index():
    job_ads_dict = get_job_ads_object()
    return render_template('home.html', job_ads_dict=job_ads_dict, login=login_or_logout())


@app.route('/accounting')
def accounting():
    job_ads_dict = get_job_ads_object()
    return render_template('accounting.html', job_data=job_ads_dict['Accounting_Finance'], accounting='active', login=login_or_logout())


@app.route('/engineering')
def engineering():
    job_ads_dict = get_job_ads_object()
    return render_template('engineering.html', job_data=job_ads_dict['Engineering'], engineering='active', login=login_or_logout())


@app.route('/healthcare')
def healthcare():
    job_ads_dict = get_job_ads_object()
    return render_template('healthcare.html', job_data=job_ads_dict['Healthcare_Nursing'], healthcare='active', login=login_or_logout())


@app.route('/hospitality')
def hospitality():
    job_ads_dict = get_job_ads_object()
    return render_template('hospitality.html', job_data=job_ads_dict['Hospitality_Catering'], hospitality='active', login=login_or_logout())


@app.route('/it')
def it():
    job_ads_dict = get_job_ads_object()
    return render_template('it.html', job_data=job_ads_dict['IT'], it='active', login=login_or_logout())


@app.route('/advertising')
def advertising():
    job_ads_dict = get_job_ads_object()
    return render_template('advertising.html', job_data=job_ads_dict['PR_Advertising_Marketing'], advertising='active', login=login_or_logout())


@app.route('/sales')
def sales():
    job_ads_dict = get_job_ads_object()
    return render_template('sales.html', job_data=job_ads_dict['Sales'], sales='active', login=login_or_logout())


@app.route('/teaching')
def teaching():
    job_ads_dict = get_job_ads_object()
    return render_template('teaching.html', job_data=job_ads_dict['Teaching'], teaching='active', login=login_or_logout())


@app.route('/about')
def about():
    return render_template('about.html', about='active', login=login_or_logout())


@app.route('/<folder>/<filename>', methods=['GET', 'POST'])
def article(folder, filename):
    job_ads_dict = get_job_ads_object()

    # Finding the job which has to be displayed based on the folder, filename and Job ID.
    job_category_ads = job_ads_dict[folder]
    required_job_data = [
        data for data in job_category_ads if data['image'].rstrip('.jpg') == filename][0]

    return render_template('article.html', required_job_data=required_job_data, login=login_or_logout())

@app.route('/search', methods=['POST'])
def search():
    # Defining porter stemmer since similar words have to be reduced to the root word for searching
    stemmer = PorterStemmer()

    # Getting the search text entered by user.
    searchText = str(request.form['search-string'])

    # Tokenising and stemming the search text
    tokenised_searchText = tokenize(searchText)
    tokenised_searchText = set([stemmer.stem(token) for token in tokenised_searchText])

    # Creating a flat list of job ads.
    job_ads_dict = get_job_ads_object()
    job_ads_flat_list = list(chain.from_iterable(job_ads_dict.values()))
    # Initialising variables for result and tokenised jobs
    matched_jobs = []
    tokenised_jobs = []

    # Looping through each of the jobs in the list
    for job_ad in job_ads_flat_list:
        # The condition is to check if the company information is present.
        if job_ad['company'] == 'Not Specified':
            # Tokenising title and description
            tokenised_title = tokenize(job_ad['title'])
            tokenised_desc = tokenize(job_ad['full_content'])

            # Stemming for title and description
            tokenised_title = [stemmer.stem(token) for token in tokenised_title]
            tokenised_desc = [stemmer.stem(token) for token in tokenised_desc]

            # Forming a combined list of job id, tokenised title and stemmed description
            tokenised_job = set(chain.from_iterable([[job_ad['id']], tokenised_title, tokenised_desc]))
            tokenised_jobs.append(tokenised_job)
        else:
            tokenised_title = tokenize(job_ad['title'])
            tokenised_company = tokenize(job_ad['company'])
            tokenised_desc = tokenize(job_ad['full_content'])

            tokenised_title = [stemmer.stem(token) for token in tokenised_title]
            tokenised_company = [stemmer.stem(token) for token in tokenised_company]
            tokenised_desc = [stemmer.stem(token) for token in tokenised_desc]

            tokenised_job = set(chain.from_iterable([[job_ad['id']], tokenised_title, tokenised_company, tokenised_desc]))
            tokenised_jobs.append(tokenised_job)
    
    # Creating a list which handles the relevance score of the jobs with respect to search string. 
    relvance_score_list = []
    
    # Looping through the processed jobs and finding the relevance scores.
    for job in tokenised_jobs:
        relevance = 0
        for search_word in tokenised_searchText:
            if search_word in job:
                relevance += 1
        relvance_score_list.append(relevance)

    # Gettng job indices having the highest relevance score with the seacrh text.
    job_ads_indices_with_highest_relevance = [indice for indice in np.flip(np.argsort(relvance_score_list)) if relvance_score_list[indice] > 0]

    # Getting the matched jobs based on the indices and omitting data with relvance score of zero.
    matched_jobs = pd.Series(job_ads_flat_list)[job_ads_indices_with_highest_relevance].to_list()

    return render_template('search.html', search_results=matched_jobs[:10], count=len(matched_jobs), searchText=searchText,  login=login_or_logout())


@app.route('/login', methods=['GET', 'POST'])
def login():
    userNamesAndPassWords = {
        'COSC2820': 'Testing',
        'Joyal': 'Testing 2',
        'Test User': 'RMIT 1'
    }

    if 'username' in session:
        if 'Post Jobs' in request.form.keys():
            return redirect('/postjobs')
        elif 'Employer Logout' in request.form.keys():
            session.pop('username', None)
            return redirect('/')
        else:
            return render_template('login.html', login=login_or_logout())
    else:
        if request.method == 'POST' and 'Post Jobs' not in request.form.keys() and 'Employer Login' not in request.form.keys():
            user_name = request.form['username']
            if (user_name in userNamesAndPassWords.keys()) and (userNamesAndPassWords[user_name] == request.form['password']):
                session['username'] = user_name
                return redirect('/postjobs')
            else:
                return render_template('login.html', login_message='Username or password is invalid.', login=login_or_logout())

    return render_template('login.html', login=login_or_logout())


@app.route('/postjobs', methods=['GET', 'POST'])
def postjobs():
    categories = [
        'Accounting_Finance',
        'Engineering',
        'Healthcare_Nursing',
        'Hospitality_Catering',
        'IT',
        'PR_Advertising_Marketing',
        'Sales',
        'Teaching'
    ]

    if 'username' in session:
        if request.method == 'POST':
            # Checking whether user has clicked on the "Classify" button
            if 'Classify' in request.form.keys():

                # Getting the form data
                job_title = request.form['title']
                job_salary = request.form['salary']
                job_company = request.form['company']
                job_description = request.form['description']

                # Tokenising title and description
                tokenised_title = tokenize(job_title)
                tokenised_desc = tokenize(job_description)

                # Reading the stopwords from the provided file.
                stop_words = set()
                with open('stopwords_en.txt') as stopwords:
                    stop_words = set([word.strip('\n') for word in stopwords])

                # Removal of stop words from the description provided
                tokenised_desc = [token for token in tokenised_desc if token not in stop_words]

                # Reading the terms occuring only once from the provided file.
                terms_with_single_occurence = set()
                with open('terms_with_single_occurence.txt') as file:
                    terms_with_single_occurence = set([word.strip('\n') for word in file])

                # Removal of terms occuring only once from the description provided
                tokenised_desc = [token for token in tokenised_desc if token not in terms_with_single_occurence]

                # Reading the terms occuring most based on document frequency from the provided file.
                words_with_high_doc_freq = set()
                with open('words_with_high_doc_freq.txt') as file:
                    words_with_high_doc_freq = set([word.strip('\n') for word in file])

                # Removal of words with most document frequency from the description provided.
                tokenised_desc = [token for token in tokenised_desc if token not in words_with_high_doc_freq]

                # Loading the saved pre trained word2vec model
                preTrained_word2vec = ""

                # Generating document vectors for title and description
                title_w2v = gen_docVecs(preTrained_word2vec, [tokenised_title])
                desc_w2v = gen_docVecs(preTrained_word2vec, [tokenised_desc])
                # Combining title and description document vectors.
                combined_vector = desc_w2v.join(title_w2v, rsuffix='-title')

                # Loading saved logistic regression model
                model = pickle.load(
                    open('model_job_ads_title_desc_w2v.sav', 'rb'))

                # Predicting the category of the job
                y_pred = model.predict(combined_vector)
                y_pred = y_pred[0]

                predicted_message = "The suggested category of this advertisement is {}.".format(
                    y_pred)

                return render_template('postjobs.html', login=login_or_logout(), predicted_message=predicted_message,
                                       title=job_title, salary=job_salary, company=job_company, description=job_description,
                                       categories=categories, predicted_category=y_pred)
            # Checking if user has clicked on the "Post Job" button
            elif "Post Job" in request.form.keys():

                # Getting the form data
                job_title = request.form['title']
                job_salary = request.form['salary']
                job_company = request.form['company']
                job_description = request.form['description']

                # Getting the category of the job. 
                job_category = request.form['categories']
                
                # Creating a set of job id's present in the system 
                job_ads_dict = get_job_ads_object()
                job_ads_flat_list = list(
                    chain.from_iterable(job_ads_dict.values()))
                job_ids_list = set([ad['id'] for ad in job_ads_flat_list])

                # Assigning a new id to the job getting added and ensuring new id is unique in the system.
                new_id_found = False
                while not new_id_found:
                    random_id = random.randint(10000, 99999)
                    if random_id not in job_ids_list:
                        new_id_found = True
                        job_id = random_id

                # Generating the data to be printed onto the file.
                dataToPrint = f'Title: {job_title}\n'
                if len(str(job_salary).strip()):
                    dataToPrint += f'Salary: {job_salary}\n'
                if len(str(job_company).strip()):
                    dataToPrint += f'Company: {job_company}\n'
                dataToPrint +=  f'Description: {job_description}'

                # Creating the job file and adding the data.
                with open(f'data/{job_category}/Job_{job_id}.txt', 'w') as job:
                    print(dataToPrint, file=job)

                return redirect(f'/{job_category}/Job_{job_id}')
        else:
            return render_template('postjobs.html', login=login_or_logout())
    else:
        return redirect('/login')

# ===============================================Route Definitions End================================================================

# ===============================================Error Handling Start=================================================================

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# ===============================================Error Handling End===================================================================


# References

# 1. Week 7, 8, 9, 10, 11, Activities and Exercises, COSC2820, RMIT University, viewed 10th to 17th October 2021, <https://rmit.instructure.com/courses/79952/pages/week-10-overview?module_item_id=3575376>
# 2. w3schools 2021, How TO - Flip Card, w3schools, viewed 10th to 17th October 2021, <https://www.w3schools.com/howto/howto_css_flip_card.asp>
# 3. EthicalJobs 2021, EthicalJobs, viewed 12th October 2021, <https://www.ethicaljobs.com.au/>
# 4. stackoverflow 2021, Display a ‘loading’ message while a time consuming function is executed in Flask, stackoverflow, viewed 13th October 2021, <https://stackoverflow.com/questions/14525029/display-a-loading-message-while-a-time-consuming-function-is-executed-in-flask>

if __name__ == "__main__":
       app.run(port=5000)