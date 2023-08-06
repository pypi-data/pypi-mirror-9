"""

http://blast.ncbi.nlm.nih.gov/blastcgihelp.shtml
http://www.ncbi.nlm.nih.gov/toolkit/doc/book/ch_demo/?rendertype=table&id=ch_demo.T5#ch_demo.id1_fetch.html_ref_fasta

"""
from collections import OrderedDict
import pandas as pd
import pylab

__all__ = ["FASTA", "MultiFASTA"]

"""
json file like in ensembl:
    molecule (e.g., dna)
    id =

    {u'id': u'contig::ABBA01004489.1:1:100:1',
             u'molecule': u'dna',
              u'seq': u'ctgtact'}
"""


class Sequence(str):
    def __init__(self):
        self.description = None
        
    def complement(self):
        pass

    def reverse(self):
        pass



class MultiFASTA(object):
    """Class to manipulate several several FASTA items

    Here, we load some FASTA using UniProt web service::

        >>> from biokit.io import MultiFASTA
        >>> mf = MultiFASTA()
        >>> mf.load_fasta("P43408")
        >>> mf.load_fasta("P21318")

    You can then get back to your accession entries as follows ::

        >>> mf.ids
        ['P43408', 'P21318']

    And the sequences in the same order can be accessed::

        >>> len(mf)
        2

    Each FASTA is stored in :attr:`fasta`, which is a dictionary where each
    values is an instance of :class:`FASTA`::

        >>> print(mf._fasta["P43408"].fasta)
        >sp|P43408|KADA_METIG Adenylate kinase OS=Methanotorris igneus GN=adkA PE=1 SV=2
        MKNKVVVVTGVPGVGGTTLTQKTIEKLKEEGIEYKMVNFGTVMFEVAKEEGLVEDRDQMR
        KLDPDTQKRIQKLAGRKIAEMAKESNVIVDTHSTVKTPKGYLAGLPIWVLEELNPDIIVI
        VETSSDEILMRRLGDATRNRDIELTSDIDEHQFMNRCAAMAYGVLTGATVKIIKNRDGLL
        DKAVEELISVLK

    The most convenient way to access to all data is to use the dataframe attribute::

        >>> mf.df.Sequence


    .. plot::
        :width: 50%
        :include-source:

        >>> from bioservices.apps import MultiFASTA
        >>> f = MultiFASTA()
        >>> f.load_fasta(["P43403", "P43410"])
        >>> f.df.Size.hist()

    """
    def __init__(self, verbose=True):
        # fetch the sequence using this attribute
        self.verbose = verbose
        self._fasta_fetcher = FASTA()

        # an ordered dictionary to store the fasta contents
        self._fasta = OrderedDict()

    def __len__(self):
        return len(self._fasta)

    def _get_fasta(self):
        return self._fasta
    fasta = property(_get_fasta, doc="Returns all FASTA instances ")

    def _get_ids(self):
        return [f for f in self._fasta.keys()]
    ids = property(_get_ids, doc="returns list of keys/accession identifiers")


    def load_fasta(self, ids):
        """Loads a single FASTA file into the dictionary

        """
        if isinstance(ids, str):
            ids = [ids]

        for id_ in ids:
            self._fasta_fetcher.load(id_)
            # create a new instance of FASTA and save fasta data
            f = FASTA()
            f._fasta = self._fasta_fetcher._fasta[:]

            # append in the ordered dictionary
            self._fasta[id_] = f
            if self.verbose:
                print("%s loaded" % id_)

    def save_fasta(self, filename):
        """Save all FASTA into a file"""
        fh = open(filename, "w")
        for f in self._fasta.values():
            fh.write(f.fasta)
        fh.close()

    def read_fasta(self, filename):
        """Load several FASTA from a filename"""
        fh = open(filename, "r")
        data = fh.read()
        fh.close()

        # we split according to ">2 character
        for thisfasta in data.split(">")[1:]:
            f = FASTA()
            f._fasta = f._interpret(thisfasta)
            try:print(f.accession, self.ids)
            except:pass
            if f.accession != None and f.accession not in self.ids:
                self._fasta[f.accession] = f
            else:
                if self.verbose:
                    print("Accession %s is already in the ids list or could not be interpreted. skipped" % str(f.accession))

    def _get_df(self):
        df =  pd.concat([self.fasta[id_].df for id_ in self.fasta.keys()])
        df.reset_index(inplace=True)
        return df
    df = property(_get_df)

    def hist_size(self, **kargs):
        self.df.Size.hist(**kargs)
        pylab.title("Histogram length of the sequences")
        pylab.xlabel("Length")


class FASTA(object):
    """Dedicated class to manipulates FASTA sequence(s)

    Here is a FASTA file example::

        >sp|P43408|KADA_METIG Adenylate kinase OS=Methanotorris igneus GN=adkA PE=1 SV=2
        MKNKVVVVTGVPGVGGTTLTQKTIEKLKEEGIEYKMVNFGTVMFEVAKEEGLVEDRDQMR
        KLDPDTQKRIQKLAGRKIAEMAKESNVIVDTHSTVKTPKGYLAGLPIWVLEELNPDIIVI
        VETSSDEILMRRLGDATRNRDIELTSDIDEHQFMNRCAAMAYGVLTGATVKIIKNRDGLL
        DKAVEELISVLK

    Comments can be added with the ; character. Note also that length of the sequence
    is wrapped to 80 characters in general.

    The format is made of a header and a sequence. Any FASTA can be read
    and the pair of header/sequence retrieved from the :attr:`sequence` and
    :attr:`header` attributes. However, headers differ from one database to
    another one (see table below)

    Wikipedia. A multiple sequence FASTA format would be obtained by concatenating several single sequence FASTA files. This does not imply a contradiction with the format as only the first line in a FASTA file may start with a ";" or ">", hence forcing all subsequent sequences to start with a ">" in order to be taken as different ones (and further forcing the exclusive reservation of ">" for the sequence definition line). Thus, the examples above may as well be taken as a multisequence file if taken together.

    You can read a FASTA sequence from a local file, a string or download one 
    from UniProt using BioServices::

    .. doctest::

        >>> from biokit.io.fasta import FASTA
        >>> f = FASTA()
        >>> f.load("P43403")
        >>> acc = f.accession    # the accession (P43403)
        >>> fasta = f.fasta      # raw FASTA string
        >>> seq = f.sequence     # the sequence itself
        >>> header = f.header    # the header itself
        >>> identifier = f.identifier

    You can also get a dataframe also using Pandas library.::

        >>> f.df

    The columns stored in the dataframe encompase:

        * **Accession** that is taken from the header (e.g., P43403 from uniprot)
        * **Sequence**, a copy of the FASTA sequence
        * **Size**,  the length of the sequence.
        * **Database**, the database type found in the header (e.g., sp for
          SWISS-PROT; see below for a list of database and their header format).
        * Some column such as **Organism** are filled only for some database
        * **Identififers** is the begining of the header.

    .. seealso:: :class:`MultiFASTA` for multi FASTA manipulation.

    List of identifiers corresponding to different databases.

    ================================= ====================================
    ================================= ====================================
    GenBank                           gi|gi-number|gb|accession|locus
    GenBank                           gb|accession|locus
    GenInfo integrated database       gi|integer
    EMBL Data Library                 gi|gi-number|emb|accession|locus
    EMBL Data Library                 emb|accession|locus
    DDBJ, DNA Database of Japan       gi|gi-number|dbj|accession|locus
    DDBJ, DNA Database of Japan       dbj|accession|locus
    NBRF PIR                          pir||entry
    PIR                               pir|accession|name
    Protein Research Foundation       prf||name
    PRF                               prf|accession|name
    SWISS-PROT                        sp|accession|name
    Brookhaven Protein Data Bank (1)  pdb|entry|chain
    Brookhaven Protein Data Bank (2)  entry:chain|PDBID|CHAIN|SEQUENCE
    Patents                           pat|country|number
    patent                            pat|country|patent|sequence
    pre-grant patent                  pgp|country|application-number|seq-number
    GenInfo Backbone Id               bbs|number
    GenInfo Backbone moltype          bbm|number
    GenInfo import ID                 gim|integer
    General database identifier       gnl|database|identifier
    NCBI Reference Sequence           ref|accession|locus
    RefSeq 2                          ref|accession|name
    Local Sequence identifier         lcl|identifier
    PDB                               pdb|entry|chain
    DDBJ                              dbj|accession|locus  
    Default                           |accession|name
    ================================= ====================================

identifier is mix of integers and characters




    gnl allows databases not included in this list to use the same identifying syntax.

    The :meth::`load_fasta` relies on UniProt service.
    """

    known_dbtypes = ["sp", "gi"]
    def __init__(self):
        self._fasta = None

    def _get_fasta(self):
        return self._fasta
    fasta = property(_get_fasta, doc="returns FASTA content")

    # for all types
    def _get_sequence(self):
        if self.fasta:
            return "".join(self.fasta.split("\n")[1:])
        else:
            raise ValueError("You need to load a fasta sequence first using get_fasta or read_fasta")
    sequence = property(_get_sequence, doc="returns the sequence only")

    # for all types
    def _get_header(self):
        if self.fasta:
            return self.fasta.split("\n")[0]
        else:
            raise ValueError("You need to load a fasta sequence first using get_fasta or read_fasta")
    header = property(_get_header, doc="returns header only")

    def _get_dbtype(self):
        dbtype = self.header.split("|")[0].replace(">", "")
        return dbtype
    dbtype = property(_get_dbtype)

    # for all types
    def _get_identifier(self):
        return self.header.split(" ")[0]
    identifier = property(_get_identifier)

    def _get_entry(self):
        return self.header.split("|")[2].split(" ")[0]
    entry = property(_get_entry, doc="returns entry only")

    # swiss prot only
    def _get_accession(self):
        if self.dbtype == "sp":
            #header = self.header
            return self.identifier.split("|")[1]
        elif self.dbtype == "gi":
            return self.identifier.split("|")[1]

    accession = property(_get_accession)

    # swiss prot only
    def _get_name_sp(self):
        if self.dbtype == "sp":
            header = self.header
            return header.split(" ")[0].split("|")[2]
    name = property(_get_name_sp)

    def _get_df(self):
        df = pd.DataFrame({
            "Identifiers": [self.identifier],
            "Accession": [self.accession],
            "Entry": [self.entry],
            "Database": [self.dbtype],
            "Organism": [self.organism],
            "PE": [self.PE],
            "SV": [self.SV],
            "Sequence": [self.sequence],
            "Header": [self.header],
            "Size": [len(self.sequence)]})
        return df
    df = property(_get_df)

    def _get_info_from_header(self, prefix):
        if prefix not in self.header:
            return None
        # finds the prefix
        index = self.header.index(prefix+"=")
        # remove it
        name = self.header[index:][3:]
        # figure out if there is anothe = sign to split the string
        # otherwise, the prefix we looked for is the last one anyway
        if "=" in name:
            name = name.split("=")[0]
            # here each = sign in FASTA is preceded by 2 characters that we must remove
            name = name[0:-2]
            name = name.strip()
        else:
            name = name.strip()
        return name

    def _get_gene_name(self):
        return self._get_info_from_header("GN")
    gene_name = property(_get_gene_name,
        doc="returns gene name from GN keyword found in the header if any")

    def _get_organism(self):
        return self._get_info_from_header("OS")
    organism = property(_get_organism,
        doc="returns organism from OS keyword found in the header if any")

    def _get_PE(self):
        pe = self._get_info_from_header("PE")
        if pe is not None:
            return int(pe)
    PE = property(_get_PE,
        doc="returns PE keyword found in the header if any")

    def _get_SV(self):
        sv = self._get_info_from_header("SV")
        if sv is not None:
            return int(sv)
    SV = property(_get_SV,
        doc="returns SV keyword found in the header if any")

    def __str__(self):
        str_ = self.fasta
        return str_

    def load(self, id_):
        self.load_fasta(id_)

    def load_fasta(self, id_):
        """Fetches FASTA from uniprot and loads into attribute :attr:`fasta`

        :param str id_: a given uniprot identifier
        :returns: nothing

        .. note:: same as :meth:`get_fasta` but returns nothing
        """
        # save fasta into attributes fasta
        from bioservices import UniProt
        u = UniProt(verbose=False)
        try:
            res = u.retrieve(id_, frmt="fasta")
            # some entries in uniprot are valid but obsolet and return empty string
            if res == "":
                raise Exception
            self._fasta = res[:]
        except:
            pass

    def save_fasta(self, filename):
        """Save FASTA file into a filename

        :param str data: the FASTA contents
        :param str filename: where to save it
        """
        if self._fasta == None:
            raise ValueError("No fasta was read or downloaded. Nothing to save.")

        fh = open(filename, "w")
        fh.write(self._fasta)
        fh.close()

    def read_fasta(self, filename):
        """Reads a FASTA file and loads it

        Type::

            >>> f = FASTA()
            >>> f.read_fasta(filename)
            >>> f.fasta

        :return: nothing

        .. warning:: If more than one FASTA is contained in the file, an error is raised
        """
        fh = open(filename, "r")
        data = fh.read()
        fh.close()

        # Is there more than one sequence ?
        data = data.split(">")[1:]
        if len(data)>1 or len(data)==0:
            raise ValueError("""Only one sequence expected to be found. Found %s. Please use MultiFASTA class instead""" % len(data))

        self._data = data
        if data.count(">sp|")>1:
            raise ValueError("""It looks like your FASTA file contains more than
            one FASTA. You must use MultiFASTA class instead""")
        self._fasta = data[:]
        self._fasta = self._fasta[0]
        if self.dbtype not in self.known_dbtypes:
            print("Only sp and gi header are recognised so far but sequence and header are loaded")


    def _interpret(self, data):
        # cleanup the data in case of empty spaces or \n characters
        return data






    def check(self):
        """Before submitting a request, any numerical digits in the query 
        sequence should either be removed or replaced by appropriate letter 
        codes (e.g., N for unknown nucleic acid residue or X for unknown 
        amino acid residue). The nucleic acid codes supported are:
            
         For those programs that use amino acid query sequences (BLASTP 
         and TBLASTN), the accepted amino acid codes are:
         A, B, C, D, E, F, G, H, I, K, L, M, N, P, Q, R, S, T, U, V, W, Y, Z, X, *, -


         * is for translation stop and - for gap of indeterminate length
                                                                                                                        
        """
        pass




