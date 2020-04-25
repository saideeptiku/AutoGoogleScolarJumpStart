import scholarly
import refextract
import os

def get_refs(file_path):
    """list of references in pdf file"""
    print("File:", file_path)
    refs = refextract.extract_references_from_file(str(file_path))

    # iterate over refs
    for i, ref in enumerate(refs):

        # skip this if this is a link
        if "http" in "".join(ref['raw_ref']):
            continue
        
        # get title of this work
        title = ref.get('title', None)

        # if not none pass on
        # if title was read
        if title is not None:
            title = " ".join(title).lower()
            yield title
    

def get_files(folder):
    """get all files under folder"""

    # iter over each file
    for f in os.listdir(folder):

        # check if this is a pdf
        if f.split(".")[-1] == "pdf":
            yield folder + "/" + f

            
if __name__ == "__main__":

    titles = []
    
    # get this file
    for fp in get_files("files"):
       
        # get title
        for title in get_refs(fp):

            titles.append(title)

    print(f"found {len(set(titles))} titles.")


    for title in titles:
        # looking up title on google scolar
        # assume feeling lucky
        print(f"searching: {title}")
        #try:
        pub = next(scholarly.search_pubs_query(title)).fill()
        #except Exception as E:
        #    print(E)
        #    pub = None
        
        print(f"found: {pub}", end="\n\n")
