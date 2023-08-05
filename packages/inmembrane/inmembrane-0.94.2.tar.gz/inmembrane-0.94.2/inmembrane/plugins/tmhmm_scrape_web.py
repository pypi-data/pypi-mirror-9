# -*- coding: utf-8 -*-
citation = {'ref': u"Anders Krogh, Björn Larsson, Gunnar von Heijne and Erik "
                   u"L. L. Sonnhammer (2001) Predicting Transmembrane Protein "
                   u"Topology with a Hidden Markov Model: Application to "
                   u"Complete Genomes. J. Mol. Biol. 305:567-580. \n"
                   u"<http://dx.doi.org/10.1006/jmbi.2000.4315>",
            'name': "TMHMM 2.0"
           }
          
__DEBUG__ = True

import sys, os, time
from StringIO import StringIO
from BeautifulSoup import BeautifulSoup
import requests

try:
  from collections import OrderedDict
except:
  from ordereddict import OrderedDict

import inmembrane
from inmembrane.plugins.tmhmm import parse_tmhmm
from inmembrane.helpers import log_stderr
from inmembrane.helpers import generate_safe_seqids, proteins_to_fasta

def annotate(params, proteins, \
             batchsize=500, \
             force=False):
  """
  This plugin inferfaces with the TMHMM web interface (for humans) and
  scrapes the results. This is a silly way to do it, since there is
  a SOAP service ... however when the SOAP service goes down, as it does
  from time to time, this plugin can be used as a stopgap.
  """

  baseurl = "http://www.cbs.dtu.dk"
  url = baseurl + "/cgi-bin/nph-webface"

  # grab the cached results if present
  outfile = "tmhmm_scrape_web.out"
  if not force and os.path.isfile(outfile):
    log_stderr("# -> skipped: %s already exists" % outfile)
    proteins, id_mapping = generate_safe_seqids(proteins)
    fh = open(outfile, 'r')
    resultpage = fh.read()
    fh.close()
    #soup = BeautifulSoup(resultpage)
    proteins = parse_tmhmm(resultpage, proteins, id_mapping=id_mapping)
    return proteins

  proteins, id_mapping = generate_safe_seqids(proteins)

  seqids = proteins.keys()
  allresultpages = ""
  while seqids:
    seqid_batch = seqids[0:batchsize]
    del seqids[0:batchsize]

    # get batch of sequences in fasta format with munged ids 
    # (workaround for potential tmhmm sequence id munging)
    safe_fasta = proteins_to_fasta(proteins, seqids=seqid_batch, 
                                             use_safe_seqid=True)

    # we use an OrderedDict rather than a normal dictionary to work around 
    # some quirks in the CBS CGI (the server expects parameters in a certain 
    # order in the HTTP headers).
    payload = OrderedDict([('configfile',
                          "/usr/opt/www/pub/CBS/services/TMHMM-2.0/TMHMM2.cf"),
                          ("SEQ",""),
                          ("outform","-noplot")])

    #files = {'seqfile': open(params['fasta'], 'rb')}
    files = {'seqfile': StringIO(safe_fasta)}

    log_stderr("# TMHMM(scrape_web), %s > %s" % (params['fasta'], outfile))

    headers = {"User-Agent": 
               "python-requests/%s (inmembrane/%s)" % 
               (requests.__version__, inmembrane.__version__) }
    r_post = requests.post(url, data=payload, files=files, headers=headers)

    # HACK: the initial POST throws us a 302 redirect and we grab the redirect url from the text
    #       (... not sure why requests allow_redirect=True option doesn't handle this transparently)
    pollingurl = r_post.url + r_post.text.split("Location: ")[1]
    r = requests.get(pollingurl)

    if __DEBUG__:
      log_stderr(r.text)
      # Example:
      #
      # <HTML>
      # <HEAD><TITLE>Webface Jobsubmission</TITLE></HEAD>
      # If Javascript is disabled, follow <a href="/cgi-bin/nph-webface?jobid=TMHMM2,50B5432A10A9CD51&opt=wait">This link</a>
      #
      # <script LANGUAGE="JavaScript"><!--
      # location.replace("/cgi-bin/nph-webface?jobid=TMHMM2,50B5432A10A9CD51&opt=wait")
      # //--></script>
      # </HTML>

    # extract the result URL (or die if job is rejected ...)
    if "Job rejected" in r.text:
      sys.stderr.write(r.text)
      sys.exit()

    # sometimes we get a polling page, other times the result page is sent immediately.
    if ("<title>Job status of" in r.text):
      r = r.text.replace("<noscript>","").replace("</noscript","")
      soup = BeautifulSoup(r)
      resultlink = soup.findAll('a')[0]['href']
      if __DEBUG__:
        log_stderr(resultlink)

      # try grabbing the result, then keep polling until they are ready
      sys.stderr.write("# Waiting for TMHMM(scrape_web) results")
      time.sleep(len(proteins)/500)
      resultpage = requests.get(resultlink).text
      retries = 0
      while ("<title>Job status of" in resultpage) and retries < 10:
        sys.stderr.write(".")
        time.sleep(len(proteins)/100 + retries**2)
        resultpage = requests.get(resultlink).text
        retries += 1
    else:
      resultpage = r.text

    sys.stderr.write(" .. done !\n")

    if __DEBUG__:
      log_stderr(resultpage)

    allresultpages += clean_result_page(resultpage)
  
  # we store the cleaned up result pages concatenated together
  fh = open(outfile, 'a+')
  fh.write(allresultpages)
  fh.close()

  proteins = parse_tmhmm(allresultpages, proteins, id_mapping=id_mapping)
  return proteins

def clean_result_page(resultpage):
  """
  Takes the HTML output from the TMHMM result page and trims some HTML
  to make the output parsable by the existing standalone tmhmm parser.

  Returns the cleaned up result page.
  """
  resultlines = resultpage.split('\n')
  firstpreindex = 0
  # find first pre-tag
  for i in range(len(resultlines)):
    if "<pre>" in resultlines[i]:
      firstpreindex = i
      break

  resultpage = "\n".join(resultlines[firstpreindex:-3])

  resultpage = resultpage.replace("<hr>", '\n')
  resultpage = resultpage.replace("<P>", '')
  resultpage = resultpage.replace("<pre>", '')
  resultpage = resultpage.replace("</pre>", '')
 
  return resultpage
