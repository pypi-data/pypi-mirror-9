# get files (you probably already have them)
wget https://sourcefile.location.org/file.txt

# install west_enrich
python setup.py install --user

# update all source documents
west_enrich --update=all
# OR
west_enrich -u all
# OR specifics 'go', 'omim', or 'kegg'
west_enrich -u go

#run
west_enrich -i [fullpath/clusterdocument.txt] -o [fullpath/outputdocument.txt] -e [go/omim/kegg] -n [fullpath/allnodesinnetwork.txt]
