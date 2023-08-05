scielo.packtools
================

Canivete suiço para a inspeção de pacotes SPS.


Instalação
----------

Python Package Index (recomendado):

```bash
pip install packtools
```

Pip + git (versão de desenvolvimento):

```bash
pip install -e git+git://github.com/scieloorg/packtools.git#egg=packtools
```

Repositório de códigos (versão de desenvolvimento):

```bash
git clone https://github.com/scieloorg/packtools.git
cd packtools 
python setup.py install
```


Configuração do Catálogo XML
----------------------------

Um Catálogo XML é um mecanismo de *lookup* que pode ser utilizado para evitar que requisições de 
rede sejam realizadas para carregar DTDs externas. 

Por questões de desempenho e segurança, as instâncias de `stylechecker.XML` não realizam 
conexões de rede, portanto é extremamente recomendável que seja configurado um Catálogo XML,
que traduz ids públicos para uris de arquivos locais.

O `packtools` já apresenta um catálogo padrão, que para ser utilizado basta definir a
variável de ambiente `XML_CATALOG_FILES` com o caminho absoluto para 
`packtools/catalogs/scielo-publishing-schema.xml`.

Mais informações em http://xmlsoft.org/catalog.html#Simple


Utilitário `stylechecker`
-------------------------

Após a instalação, o programa `stylechecker` deverá estar disponível no seu emulador de terminal. 
Esse programa realiza a validação de um determinado XML no formato SPS contra a DTD, e 
apresenta uma lista dos erros encontrados. Também é possível *anotar* os erros encontrados em uma
cópia do XML em validação, por meio do argumento opcional `--annotated`.

O utilitário `stylechecker` tenta carregar a DTD externa, especificada na declaração DOCTYPE do 
XML. Para evitar esse comportamento, utilize a opção `--nonetwork`.

```bash
$ stylechecker -h
usage: stylechecker [-h] [--annotated] [--nonetwork] [--version] xmlpath

stylechecker cli utility.

positional arguments:
  xmlpath      Filesystem path or URL to the XML file.

optional arguments:
  -h, --help   show this help message and exit
  --annotated
  --nonetwork
  --version    show program's version number and exit
```

Obs.: Para validar XMLs disponíveis via http, é necessário delimitar a URL com aspas ou apóstrofo. e.g.: 

```bash
$ stylechecker "http://192.168.1.162:7000/api/v1/article?code=S1516-635X2014000100012&format=xmlrsps"
Valid XML! ;)
Invalid SPS Style! Found 3 errors:
Element 'journal-meta': Missing element journal-id of type "nlm-ta" or "publisher-id".
Element 'journal-title-group': Missing element abbrev-journal-title of type "publisher".
Element 'journal-meta': Missing element issn of type "epub".
```



History
=======

0.6.2 (2015-01-23)
------------------

* Added method `XMLValidator.lookup_assets`.
* Added property `XMLValidator.assets`. 
* Fixed minor issue that would cause //element-citation[@publication-type="report"] 
  to be reported as invalid.
* Fixed minor issue that would erroneously identify an element-citation element 
  as not being child of element ref.


0.6.1 (2014-11-28)
------------------

* Minor fix to implement changes from SciELO PS 1.1.1.


0.6 (2014-10-28)
----------------

* Python 3 support.
* Project-wide code refactoring.
* `packtools.__version__` attribute to get the package version.
* Distinction between classes of error with the attribute `StyleError.level`.


0.5 (2014-09-29)
----------------

* Basic implementation of XML style rules according to SciELO PS version 1.1.
* `stylechecker` and `packbuilder` console utilities.
* Major performance improvements on `XMLValidator` instantiation, when used
  with long-running processes (9.5x).



