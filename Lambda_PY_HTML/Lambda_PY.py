def pmParse(database,query,rmax,sort,n_sent):
    from Bio import Medline
    from Bio import Entrez
    import heapq
    import time
    #Set Email and execute Query to find prospective PMIDs
    Entrez.email = "youremail@domain.com"
    search_terms=["AB","TI","DP"]
    key_mapping = {'AB': 'Abstract','TI': 'Title','DP': 'Date'}
    
    if rmax == "":
        rmax = 5
    try:
        if query == "":
            raise ValueError("Query cannot be empty, you must search something.")
        z = Entrez.esearch(db=str(database),term=str(query),rettype="json",retmode="text",sort=str(sort),retmax=int(rmax))
    except Exception as e:
        return(str(e))
    #Build list of PMIDs to inspect
    PMIDs = []
    for ele in z:
        ot="".join(ele.decode("utf-8"))
        if ot.startswith("<Id>"):
            sout = ot[4:ot.index("</Id>")]
            PMIDs.append(sout)
    
    #Execute search for PMIDs, extract title/abstract/year
    dicto = {}
    for PMID in PMIDs:
        handle = Entrez.efetch(db=database, id=PMID, rettype="medline", retmode="text")
        records = Medline.parse(handle)
        for ele in records:
            temp = {key_mapping[term] : ele[term] for term in search_terms if term in ele}
        if not "Date" in temp.keys():
            temp["Date"]="NA"
        dicto[PMID] = temp
        print("Completed Parsing, waiting 1 seconds")
        time.sleep(1)
    
    #Organize and present information in HTML
    summariesDicto = {}
    for PMID in dicto.keys():
        try:
            sentScores = score_sentences(dicto[PMID]['Abstract'])
        except:
            continue
        sentScores = dict(zip(sentScores[1],sentScores[0].values()))
        summary_sentences = heapq.nlargest(int(n_sent), sentScores, key=sentScores.get)
        summary = ' '.join(summary_sentences)
        summariesDicto[PMID] = summary
    return(summariesDicto,dicto)

def score_sentences(inp):
    import nltk
    import re
    nltk.data.path.append('/opt/python/lib/python3.9/site-packages/nltk_data')
    from nltk.corpus import stopwords                       
    from nltk.tokenize import word_tokenize, sent_tokenize
    stopWords = set(stopwords.words("english"))
    sentsb4 = sent_tokenize(inp)
    text = inp
    text = re.sub(r'\[[0-9]*\]|[^a-zA-Z0-9. ]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    words,sents = word_tokenize(text),sent_tokenize(text)
    
    freqTable = {}               
    for word in words:                                
        if word not in stopWords:
            #word = word.lower()
            if word in freqTable:                       
                freqTable[word.lower()] += 1            
            else:          
                freqTable[word.lower()] = 1
    max_freq = max(freqTable.values())
    for k,v in freqTable.items():
        freqTable[k] = v/max_freq
    
    sentScores = {}
    for sent in sents:
        for vurd in word_tokenize(sent.lower()):
            if vurd in freqTable.keys():
                if sent not in sentScores.keys():
                    sentScores[sent] = freqTable[vurd]
                else:
                    sentScores[sent] += freqTable[vurd]
    out = [sentScores,sentsb4]
    return(out)
    
def get_key(form_data):
    key = form_data.split(";")[1].split("=")[1].replace('"', '')
    return(key)
    
def place_tboxes(html, outdict, outdict2, meta):
    replacement_html = f"<h3>Your query was: {meta[0]} | Your database was: {meta[1]}</h3>"
    for k, v in outdict.items():
        replacement_html += f"""
        <div style="border: 1px solid black; padding: 10px; margin: 10px;">
            <h3>ID: {k} | Title: {outdict2[k]['Title']} | Publication Date: {outdict2[k]['Date']}</h3>
            <p>{v}</p>
        </div>
        """
    rehtml = html.replace("<h3>{replaceme}</h3>", replacement_html)
    return(rehtml)
