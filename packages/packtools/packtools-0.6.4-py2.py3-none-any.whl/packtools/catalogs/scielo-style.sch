<?xml version="1.0" encoding="utf-8"?>
<schema xmlns="http://purl.oclc.org/dsdl/schematron"
        queryBinding="xslt"
        xml:lang="en">
  <ns uri="http://www.w3.org/1999/xlink" prefix="xlink"/>
  <p>
  *******************************************************************************
   THINGS TO BE SURE BEFORE EDITING THIS FILE!

   The spec used is ISO-Schematron. 
   
   Some useful info:
     - The query language used is the extended version of XPath specified in XSLT.
     - The rule context is interpreted according to the Production 1 of XSLT. 
       The rule context may be the root node, elements, attributes, comments and 
       processing instructions. 
     - The assertion test is interpreted according to Production 14 of XPath, as 
       returning a Boolean value.

   For more info, refer to the official ISO/IEC 19757-3:2006(E) standard.
  
   The implementation of the schematron patterns comes with the idea of SPS as a
   set of constraints on top of JATS' Publishing Tag Set v1.0 (JPTS)[1]. To keep
   consistency, please make sure:
  
     - DTD/XSD constraints are not duplicated here
     - There is an issue at http://git.io/5EcR4Q with status `Aprovada`
     - PMC-Style compatibility is maintained[2]
  
   Always double-check the JPTS and PMC-Style before editing.
   [1] http://jats.nlm.nih.gov/publishing/tag-library/1.0/
   [2] https://www.ncbi.nlm.nih.gov/pmc/pmcdoc/tagging-guidelines/article/tags.html
  *******************************************************************************
  </p>

  <!--
   Phases - sets of patterns.
   These are being used to help on tests isolation.
  -->
  <phase id="phase.journal-id">
    <active pattern="journal-id_type_nlm-ta_or_publisher-id"/>
  </phase>

  <phase id="phase.journal-title-group">
    <active pattern="has_journal-title_and_abbrev-journal-title"/>
  </phase>

  <phase id="phase.publisher">
    <active pattern="publisher"/>
  </phase>

  <phase id="phase.article-categories">
    <active pattern="article_categories"/>
  </phase>

  <phase id="phase.fpage_or_elocation-id">
    <active pattern="fpage_or_elocation_id"/>
  </phase>

  <phase id="phase.issn">
    <active pattern="issn_pub_type_epub_or_ppub"/>
  </phase>

  <phase id="phase.article-id">
    <active pattern="has_article_id_type_doi_and_valid_values"/>
  </phase>

  <phase id="phase.subj-group">
    <active pattern="subj_group"/>
    <active pattern="subj_group_subarticle_pt"/>
    <active pattern="subj_group_subarticle_es"/>
    <active pattern="subj_group_subarticle_en"/>
  </phase>

  <phase id="phase.abstract_lang">
    <active pattern="abstract"/>
  </phase>

  <phase id="phase.article-title_lang">
    <active pattern="article-title"/>
  </phase>

  <phase id="phase.aff_contenttypes">
    <active pattern="aff_contenttypes"/>
    <active pattern="aff_contenttypes_contribgroup"/>
  </phase>

  <phase id="phase.kwd-group_lang">
    <active pattern="kwdgroup_lang"/>
  </phase>

  <phase id="phase.counts">
    <active pattern="counts"/>
  </phase>

  <phase id="phase.pub-date">
    <active pattern="pub-date_pub_type"/>
  </phase>

  <phase id="phase.volume">
    <active pattern="volume"/>
  </phase>
  
  <phase id="phase.issue">
    <active pattern="issue"/>
  </phase>

  <phase id="phase.supplement">
    <active pattern="supplement"/>
  </phase>

  <phase id="phase.elocation-id">
    <active pattern="elocation-id"/>
  </phase>

  <phase id="phase.history">
    <active pattern="history"/>
  </phase>

  <phase id="phase.product">
    <active pattern="product"/>
    <active pattern="product_product-type_values"/>
  </phase>

  <phase id="phase.sectitle">
    <active pattern="sectitle"/>
  </phase>

  <phase id="phase.paragraph">
    <active pattern="paragraph"/>
  </phase>

  <phase id="phase.disp-formula">
    <active pattern="id_disp-formula"/>
  </phase>

  <phase id="phase.table-wrap">
    <active pattern="id_table-wrap"/>
  </phase>

  <phase id="phase.table-wrap-foot">
    <active pattern="id_table-wrap-foot"/>
  </phase>

  <phase id="phase.fig">
    <active pattern="id_fig"/>
  </phase>

  <phase id="phase.app">
    <active pattern="id_app"/>
  </phase>

  <phase id="phase.aff_id">
    <active pattern="id_aff"/>
  </phase>

  <phase id="phase.supplementary-material_id">
    <active pattern="id_supplementary-material"/>
  </phase>

  <phase id="phase.ref_id">
    <active pattern="id_ref"/>
  </phase>
  
  <phase id="phase.def-list_id">
    <active pattern="id_def-list"/>
  </phase>
  
  <phase id="phase.corresp_id">
    <active pattern="id_corresp"/>
  </phase>

  <phase id="phase.fn_id">
    <active pattern="id_fn"/>
  </phase>

  <phase id="phase.media_id">
    <active pattern="id_media"/>
  </phase>

  <phase id="phase.sec_id">
    <active pattern="id_sec"/>
  </phase>

  <phase id="phase.rid_integrity">
    <active pattern="xref-reftype-integrity-aff"/>
  </phase>

  <phase id="phase.caption">
    <active pattern="caption_title"/>
  </phase>

  <phase id="phase.license">
    <active pattern="license_attributes"/>
    <active pattern="license"/>
  </phase>

  <phase id="phase.ack">
    <active pattern="ack"/>
  </phase>

  <phase id="phase.element-citation">
    <active pattern="element-citation"/>
    <active pattern="element-citation_attributes"/>
    <active pattern="element-citation_publication-type-values"/>
  </phase>

  <phase id="phase.person-group">
    <active pattern="person-group"/>
    <active pattern="person-group-type_values"/>
  </phase>

  <phase id="phase.fn-group">
    <active pattern="fn-group"/>
    <active pattern="fn_attributes"/>
  </phase>

  <phase id="phase.xhtml-table">
    <active pattern="xhtml-table"/>
  </phase>

  <phase id="phase.supplementary-material">
    <active pattern="supplementary-material_mimetype"/>
  </phase>

  <phase id="phase.xref_reftype_integrity">
    <active pattern="xref-reftype-values"/>
  </phase>

  <phase id="phase.article-attrs">
    <active pattern="article_attributes"/>
    <active pattern="article_article-type-values"/>
    <active pattern="article_specific-use-values"/>
  </phase>

  <phase id="phase.named-content_attrs">
    <active pattern="named-content_attributes"/>
    <active pattern="named-content_content-type-values"/>
  </phase>

  <phase id="phase.month">
    <active pattern="month"/>
  </phase>

  <phase id="phase.size">
    <active pattern="size_attributes"/>
    <active pattern="size_units-values"/>
  </phase>

  <phase id="phase.list">
    <active pattern="list_attributes"/>
    <active pattern="list_list-type-values"/>
  </phase>

  <phase id="phase.media_attributes">
    <active pattern="media_attributes"/>
  </phase>

  <phase id="phase.ext-link">
    <active pattern="ext-link_href_values"/>
    <active pattern="ext-link_attributes"/>
  </phase>

  <!--
   Patterns - sets of rules.
  -->
  <pattern id="journal-id_type_nlm-ta_or_publisher-id">
    <rule context="article/front/journal-meta">
      <assert test="journal-id[@journal-id-type='nlm-ta'] or journal-id[@journal-id-type='publisher-id']">
        Element 'journal-meta': Missing element journal-id with journal-id-type=("nlm-ta" or "publisher-id").
      </assert>
      <assert test="count(journal-id) = 1">
        Element 'journal-meta': There must be exactly one element journal-id.
      </assert>
    </rule>
  </pattern>

  <pattern id="has_journal-title_and_abbrev-journal-title">
    <rule context="article/front/journal-meta">
      <assert test="journal-title-group">
        Element 'journal-meta': Missing element journal-title-group.
      </assert>
    </rule>

    <rule context="article/front/journal-meta/journal-title-group">
      <assert test="journal-title">
        Element 'journal-title-group': Missing element journal-title.
      </assert>
      <assert test="abbrev-journal-title[@abbrev-type='publisher']">
        Element 'journal-title-group': Missing element abbrev-journal-title with abbrev-type="publisher".
      </assert>
    </rule>
  </pattern>

  <pattern id="publisher">
    <rule context="article/front/journal-meta">
      <assert test="publisher">
        Element 'journal-meta': Missing element publisher.
      </assert>
    </rule>
  </pattern>

  <pattern id="article_categories">
    <rule context="article/front/article-meta">
      <assert test="article-categories">
        Element 'article-meta': Missing element article-categories.
      </assert>
    </rule>
  </pattern>

  <pattern id="fpage_or_elocation_id">
    <rule context="article/front/article-meta">
      <assert test="fpage or elocation-id">
        Element 'article-meta': Missing elements fpage or elocation-id.
      </assert>
    </rule>
  </pattern>

  <pattern id="issn_pub_type_epub_or_ppub">
    <rule context="article/front/journal-meta">
      <assert test="issn[@pub-type='epub'] or issn[@pub-type='ppub']">
        Element 'journal-meta': Missing element issn with pub-type=("epub" or "ppub").
      </assert>
    </rule>
  </pattern>

  <pattern id="has_article_id_type_doi_and_valid_values">
    <rule context="article/front/article-meta">
      <assert test="article-id">
        Element 'article-meta': Missing element article-id.
      </assert>
      <assert test="article-id[@pub-id-type='doi']">
        Element 'article-meta': Missing element article-id with pub-id-type="doi".
      </assert>
    </rule>

    <rule context="article/front/article-meta/article-id">
        <assert test="@pub-id-type='doi' or 
                      @pub-id-type='other' or 
                      @pub-id-type='publisher-id'">
        Element 'article-id', attribute pub-id-type: Invalid value "<value-of select="@pub-id-type"/>".
      </assert>
    </rule>
  </pattern>

  <pattern abstract="true" id="subj_group_base">
    <title>
      Make sure only one heading is provided per language, in subj-group.
    </title>

    <rule context="$base_context">
      <assert test="count(subj-group[@subj-group-type='heading'] | subj-group//subj-group[@subj-group-type='heading']) = 1">
        Element '<name/>': There must be only one element subj-group with subj-group-type="heading".
      </assert>
    </rule>
  </pattern>

  <pattern is-a="subj_group_base" id="subj_group">
    <param name="base_context" value="article/front/article-meta/article-categories"/>
  </pattern>

  <pattern is-a="subj_group_base" id="subj_group_subarticle_pt">
    <param name="base_context" value="article/sub-article[@xml:lang='pt']/front-stub/article-categories"/>
  </pattern>
  <pattern is-a="subj_group_base" id="subj_group_subarticle_es">
    <param name="base_context" value="article/sub-article[@xml:lang='es']/front-stub/article-categories"/>
  </pattern>
  <pattern is-a="subj_group_base" id="subj_group_subarticle_en">
    <param name="base_context" value="article/sub-article[@xml:lang='en']/front-stub/article-categories"/>
  </pattern>
  <pattern is-a="subj_group_base" id="subj_group_subarticle_fr">
    <param name="base_context" value="article/sub-article[@xml:lang='fr']/front-stub/article-categories"/>
  </pattern>

  <pattern id="abstract">
    <rule context="article[@article-type='research-article'] | article[@article-type='review-article']">
      <assert test="count(front/article-meta/abstract) > 0">
        Element 'article-meta': Missing element abstract.
      </assert>
    </rule>
    <rule context="article/front/article-meta/abstract">
      <assert test="not(@xml:lang)">
        Element 'abstract': Unexpected attribute xml:lang.
      </assert>
    </rule>
  </pattern>

  <pattern id="article-title">
    <rule context="article/front/article-meta/title-group/article-title">
      <assert test="not(@xml:lang)">
        Element 'article-title': Unexpected attribute xml:lang.
      </assert>
    </rule>
  </pattern>

  <pattern abstract="true" id="aff_contenttypes_base">
    <rule context="$base_context/aff/institution">
      <assert test="@content-type='original' or 
                    @content-type='orgname' or
                    @content-type='orgdiv1' or
                    @content-type='orgdiv2' or
                    @content-type='orgdiv3' or
                    @content-type='normalized'">
        Element '<name/>', attribute content-type: Invalid value "<value-of select="@content-type"/>". 
      </assert>
    </rule>
    <rule context="$base_context/aff">
      <assert test="count(institution[@content-type='original']) = 1">
        Element '<name/>': Must have exactly one element institution with content-type="original".
      </assert>
    </rule>
  </pattern>

  <pattern is-a="aff_contenttypes_base" id="aff_contenttypes">
    <param name="base_context" value="article/front/article-meta"/>
  </pattern>

  <pattern is-a="aff_contenttypes_base" id="aff_contenttypes_contribgroup">
    <param name="base_context" value="article/front/article-meta/contrib-group"/>
  </pattern>

  <pattern id="kwdgroup_lang">
    <title>
      Make sure all kwd-group elements have xml:lang attribute.
    </title>

    <rule context="article/front/article-meta/kwd-group">
      <assert test="@xml:lang">
        Element 'kwd-group': Missing attribute xml:lang.
      </assert>  
    </rule>
  </pattern>

  <pattern id="counts">
    <title>
      Make sure the total number of tables, figures, equations and pages are present.
    </title>

    <rule context="article">
      <assert test="front/article-meta/counts/table-count/@count = count(//table-wrap)">
        Element 'counts': Missing element or wrong value in table-count.
      </assert>
      <assert test="front/article-meta/counts/ref-count/@count = count(//ref)">
        Element 'counts': Missing element or wrong value in ref-count.
      </assert>
      <assert test="front/article-meta/counts/fig-count/@count = count(//fig)">
        Element 'counts': Missing element or wrong value in fig-count.
      </assert>
      <assert test="front/article-meta/counts/equation-count/@count = count(//disp-formula)">
        Element 'counts': Missing element or wrong value in equation-count.
      </assert>
      <assert test="(front/article-meta/lpage = 0 and
                     front/article-meta/fpage = 0 and
                     front/article-meta/counts/page-count and
                     front/article-meta/counts/page-count/@count = 0) or 
                    ((front/article-meta/lpage - front/article-meta/fpage) + 1)">
        Element 'counts': Missing element or wrong value in page-count.
      </assert>
    </rule>
  </pattern>

  <pattern id="pub-date_pub_type">
    <title>
      Restrict the valid values of pub-date[@pub-type].
    </title>

    <rule context="article/front/article-meta/pub-date">
      <assert test="@pub-type = 'epub' or
                    @pub-type = 'epub-ppub' or
                    @pub-type = 'collection'">
        Element 'pub-date', attribute pub-type: Invalid value "<value-of select="@pub-type"/>".
      </assert>
    </rule>
  </pattern>

  <pattern id="volume">
    <title>
      Make sure the volume is present and is not empty.
    </title>

    <rule context="article/front/article-meta">
      <assert test="count(volume) = 1">
        Element 'article-meta': Missing element volume.
      </assert>
    </rule>

    <rule context="article/front/article-meta/volume">
      <assert test="string-length(.) > 0">
        Element 'volume': Element cannot be empty.
      </assert>
    </rule>
  </pattern>

  <pattern id="issue">
    <title>
      Make sure the issue is present and is not empty.
    </title>

    <rule context="article/front/article-meta">
      <assert test="count(issue) = 1">
        Element 'article-meta': Missing element issue.
      </assert>
    </rule>

    <rule context="article/front/article-meta/issue">
      <assert test="string-length(.) > 0">
        Element 'issue': Element cannot be empty.
      </assert>
    </rule>
  </pattern>

  <pattern id="supplement">
    <title>
      Make sure the supplement is not present.
    </title>

    <rule context="article/front/article-meta">
      <assert test="not(supplement)">
        Element 'article-meta': Unexpected element supplement.
      </assert>
    </rule>
  </pattern>

  <pattern id="elocation-id">
    <title>
      Allow elocation-id to be present only when fpage is absent.
    </title>

    <rule context="article/front/article-meta/elocation-id | article/back/ref-list/ref/element-citation/elocation-id">
      <assert test="not(following-sibling::fpage)">
        Element 'article-meta': Unexpected element elocation-id.
      </assert>
    </rule>
  </pattern>

  <pattern id="history">
    <title>
      Restrict the valid values of history/date/[@date-type].
    </title>

    <rule context="article/front/article-meta/history/date">
      <assert test="@date-type = 'received' or 
                    @date-type = 'accepted' or
                    @date-type = 'rev-recd'">
        Element 'date', attribute date-type: Invalid value "<value-of select="@date-type"/>".
      </assert>
    </rule>
  </pattern>

  <pattern id="product">
    <title>
      Allow product to be present only when article-type is book-review or product-review.
      Also, make sure product[@product-type='book'].
    </title>

    <rule context="article/front/article-meta/product">
      <assert test="/article[@article-type='book-review'] or
                    /article[@article-type='product-review']">
        Element 'article-meta': Unexpected element product.
      </assert>
      <assert test="@product-type">
        Element 'product': Missing attribute product-type.
      </assert>
    </rule>
  </pattern>

  <pattern id="product_product-type_values">
    <title>
      Make sure the supplied values are valid.
    </title>

    <rule context="article/front/article-meta/product[@product-type]">
      <assert test="@product-type = 'article' or
                    @product-type = 'book' or
                    @product-type = 'chapter' or
                    @product-type = 'other' or
                    @product-type = 'software'">
        Element 'product', attribute product-type: Invalid value "<value-of select="@product-type"/>".
      </assert>
    </rule>
  </pattern>

  <pattern id="sectitle">
    <title>
      Make sure all sections have a title element.
    </title>

    <rule context="article/body/sec">
      <assert test="string-length(title) > 0">
        Element 'sec': Missing element title.
      </assert>
    </rule>
  </pattern>

  <pattern id="paragraph">
    <title>
      Make sure paragraphs have no id attr.
    </title>

    <rule context="//p">
      <assert test="not(@id)">
        Element 'p': Unexpected attribute id.
      </assert>
    </rule>
  </pattern>

  <pattern abstract="true" id="id_uniqueness_and_prefix">
    <title>
      Abstract pattern to check ids uniqueness and prefix.
    </title>

    <rule context="$base_context">
      <assert test="number(substring(@id, string-length('$prefix') + 1)) = substring(@id, string-length('$prefix') + 1)">
        Element '<name/>', attribute id: Integer value is required after the prefix '<value-of select="'$prefix'"/>'.
      </assert>
      <assert test="starts-with(@id, '$prefix')">
        Element '<name/>', attribute id: Wrong id prefix at '<value-of select="@id"/>'.    
      </assert>
      <assert test="count(//*[@id=current()/@id]) = 1">
        Element '<name/>', attribute id: Duplicated id value '<value-of select="current()/@id"/>'.
      </assert>
    </rule>
  </pattern>

  <pattern is-a="id_uniqueness_and_prefix" id="id_disp-formula">
    <title>
      Element disp-formula must have unique ids, prefixed with `e`.
    </title>

    <param name="base_context" value="//disp-formula[@id]"/>
    <param name="prefix" value="e"/>
  </pattern>

  <pattern is-a="id_uniqueness_and_prefix" id="id_table-wrap">
    <title>
      Element table-wrap must have unique ids, prefixed with `t`.
    </title>

    <param name="base_context" value="//table-wrap"/>
    <param name="prefix" value="t"/>
  </pattern>

  <pattern is-a="id_uniqueness_and_prefix" id="id_table-wrap-foot">
    <title>
      Element table-wrap-foot/fn must have unique ids, prefixed with `TFN`.
    </title>

    <param name="base_context" value="//table-wrap-foot/fn[@id]"/>
    <param name="prefix" value="TFN"/>
  </pattern>

  <pattern is-a="id_uniqueness_and_prefix" id="id_fig">
    <title>
      Element fig must have unique ids, prefixed with `f`.
    </title>

    <param name="base_context" value="//fig"/>
    <param name="prefix" value="f"/>
  </pattern>

  <pattern is-a="id_uniqueness_and_prefix" id="id_app">
    <title>
      Element app must have unique ids, prefixed with `app`.
    </title>

    <param name="base_context" value="//app[@id]"/>
    <param name="prefix" value="app"/>
  </pattern>

  <pattern is-a="id_uniqueness_and_prefix" id="id_aff">
    <title>
      Element aff must have unique ids, prefixed with `aff`.
    </title>

    <param name="base_context" value="//aff"/>
    <param name="prefix" value="aff"/>
  </pattern>

  <pattern is-a="id_uniqueness_and_prefix" id="id_supplementary-material">
    <title>
      Element supplementary-material must have unique ids, prefixed with `suppl`.
    </title>

    <param name="base_context" value="//supplementary-material"/>
    <param name="prefix" value="suppl"/>
  </pattern>

  <pattern is-a="id_uniqueness_and_prefix" id="id_ref">
    <title>
      Element ref must have unique ids, prefixed with `B`.
    </title>

    <param name="base_context" value="//ref"/>
    <param name="prefix" value="B"/>
  </pattern>

  <pattern is-a="id_uniqueness_and_prefix" id="id_def-list">
    <title>
      Element def-list must have unique ids, prefixed with `d`.
    </title>

    <param name="base_context" value="//def-list[@id]"/>
    <param name="prefix" value="d"/>
  </pattern>

  <pattern is-a="id_uniqueness_and_prefix" id="id_corresp">
    <title>
      Element corresp must have unique ids, prefixed with `c`.
    </title>

    <param name="base_context" value="//corresp[@id]"/>
    <param name="prefix" value="c"/>
  </pattern>

  <pattern is-a="id_uniqueness_and_prefix" id="id_fn">
    <title>
      Element fn must have unique ids, prefixed with `fn`.
    </title>

    <param name="base_context" value="//author-notes/fn[@id] | //fn-group/fn[@id]"/>
    <param name="prefix" value="fn"/>
  </pattern>

  <pattern is-a="id_uniqueness_and_prefix" id="id_media">
    <title>
      Element media must have unique ids, prefixed with `m`.
    </title>

    <param name="base_context" value="//media[@id]"/>
    <param name="prefix" value="m"/>
  </pattern>

  <pattern is-a="id_uniqueness_and_prefix" id="id_sec">
    <title>
      Element sec must have unique ids, prefixed with `sec`.
    </title>

    <param name="base_context" value="//sec[@id]"/>
    <param name="prefix" value="sec"/>
  </pattern>

  <!-- start-block: xref @ref-type integrity -->
  <pattern abstract="true" id="xref-reftype-integrity-base">
    <title>
      Make sure all references to are reachable.
    </title>

    <rule context="//xref[@ref-type='$ref_type']">
      <assert test="@rid = $ref_elements">
        Element '<name/>', attribute rid: Mismatching id value '<value-of select="@rid"/>' of type '<value-of select="@ref-type"/>'.
      </assert>
    </rule>
  </pattern>

  <pattern is-a="xref-reftype-integrity-base" id="xref-reftype-integrity-aff">
    <param name="ref_type" value="aff"/>
    <param name="ref_elements" value="//aff/@id"/>
  </pattern>

  <pattern is-a="xref-reftype-integrity-base" id="xref-reftype-integrity-app">
    <param name="ref_type" value="app"/>
    <param name="ref_elements" value="//app/@id"/>
  </pattern>

  <pattern is-a="xref-reftype-integrity-base" id="xref-reftype-integrity-author-notes">
    <param name="ref_type" value="author-notes"/>
    <param name="ref_elements" value="//author-notes/@id"/>
  </pattern>

  <pattern is-a="xref-reftype-integrity-base" id="xref-reftype-integrity-bibr">
    <param name="ref_type" value="bibr"/>
    <param name="ref_elements" value="//ref/@id | //element-citation/@id | //mixed-citation/@id"/>
  </pattern>

  <pattern is-a="xref-reftype-integrity-base" id="xref-reftype-integrity-contrib">
    <param name="ref_type" value="contrib"/>
    <param name="ref_elements" value="//contrib/@id"/>
  </pattern>

  <pattern is-a="xref-reftype-integrity-base" id="xref-reftype-integrity-corresp">
    <param name="ref_type" value="corresp"/>
    <param name="ref_elements" value="//corresp/@id"/>
  </pattern>

  <pattern is-a="xref-reftype-integrity-base" id="xref-reftype-integrity-disp-formula">
    <param name="ref_type" value="disp-formula"/>
    <param name="ref_elements" value="//disp-formula/@id"/>
  </pattern>

  <pattern is-a="xref-reftype-integrity-base" id="xref-reftype-integrity-fig">
    <param name="ref_type" value="fig"/>
    <param name="ref_elements" value="//fig/@id | //fig-group/@id"/>
  </pattern>

  <pattern is-a="xref-reftype-integrity-base" id="xref-reftype-integrity-fn">
    <param name="ref_type" value="fn"/>
    <param name="ref_elements" value="//fn/@id"/>
  </pattern>

  <pattern is-a="xref-reftype-integrity-base" id="xref-reftype-integrity-sec">
    <param name="ref_type" value="sec"/>
    <param name="ref_elements" value="//sec/@id"/>
  </pattern>

  <pattern is-a="xref-reftype-integrity-base" id="xref-reftype-integrity-supplementary-material">
    <param name="ref_type" value="supplementary-material"/>
    <param name="ref_elements" value="//supplementary-material/@id"/>
  </pattern>

  <pattern is-a="xref-reftype-integrity-base" id="xref-reftype-integrity-table">
    <param name="ref_type" value="table"/>
    <param name="ref_elements" value="//table-wrap/@id | //table-wrap-group/@id"/>
  </pattern>

  <pattern is-a="xref-reftype-integrity-base" id="xref-reftype-integrity-table-fn">
    <param name="ref_type" value="table-fn"/>
    <param name="ref_elements" value="//table-wrap-foot/fn/@id"/>
  </pattern>
  <!-- end-block -->

  <pattern id="xref-reftype-values">
    <title>
      Validate the ref-type value against a list.
    </title>

    <rule context="//xref[@ref-type]">
      <assert test="@ref-type = 'aff' or
                    @ref-type = 'app' or
                    @ref-type = 'author-notes' or
                    @ref-type = 'bibr' or 
                    @ref-type = 'contrib' or
                    @ref-type = 'corresp' or
                    @ref-type = 'disp-formula' or
                    @ref-type = 'fig' or 
                    @ref-type = 'fn' or
                    @ref-type = 'sec' or
                    @ref-type = 'supplementary-material' or
                    @ref-type = 'table' or
                    @ref-type = 'table-fn'">
        Element 'xref', attribute ref-type: Invalid value "<value-of select="@ref-type"/>".
      </assert>
    </rule>
  </pattern>

  <pattern id="caption_title">
    <title>
      Make sure all captions have a title element.
    </title>

    <rule context="//caption">
      <assert test="title and string-length(title) > 0">
        Element 'caption': Missing element title.
      </assert>
    </rule>
  </pattern>

  <pattern id="license_attributes">
    <title>
      Make sure all mandatory attributes are present
    </title>

    <rule context="article/front/article-meta/permissions/license">
      <assert test="@license-type">
        Element 'license': Missing attribute license-type.
      </assert>
      <assert test="@xlink:href">
        Element 'license': Missing attribute xlink:href.
      </assert>
    </rule>
  </pattern>

  <pattern id="license">
    <title>
      Make sure the document has a permissions element, and a valid
      license (represented as a known href).

      Valid licenses are:
        - http://creativecommons.org/licenses/by-nc/4.0/
        - http://creativecommons.org/licenses/by-nc/3.0/
        - http://creativecommons.org/licenses/by/4.0/
        - http://creativecommons.org/licenses/by/3.0/
    </title>

    <rule context="article/front/article-meta">
      <assert test="permissions">
        Element 'article-meta': Missing element permissions.
      </assert>
    </rule>

    <rule context="article/front/article-meta/permissions">
      <assert test="license">
        Element 'permissions': Missing element license.
      </assert>
    </rule>

    <rule context="article/front/article-meta/permissions/license[@license-type and @xlink:href]">
      <assert test="@license-type = 'open-access'">
        Element 'license', attribute license-type: Invalid value '<value-of select="@license-type"/>'.
      </assert>
      <assert test="@xlink:href = 'http://creativecommons.org/licenses/by-nc/4.0/' or 
                    @xlink:href = 'http://creativecommons.org/licenses/by-nc/3.0/' or
                    @xlink:href = 'http://creativecommons.org/licenses/by/4.0/' or
                    @xlink:href = 'http://creativecommons.org/licenses/by/3.0/'">
        Element 'license', attribute xlink:href: Invalid value '<value-of select="@xlink:href"/>'.
      </assert>
    </rule>
  </pattern>

  <pattern id="ack">
    <title>
      Ack elements cannot be organized as sections (sec).
    </title>

    <rule context="article/back/ack">
      <assert test="not(sec)">
          Element 'ack': Unexpected element sec.
      </assert>
    </rule>
  </pattern>

  <pattern id="element-citation">
    <title>
      - Make sure name, etal and collab are not child of element-citation.
      - element-citation can be only child of ref elements.
    </title>

    <rule context="article/back/ref-list/ref/element-citation">
      <assert test="not(name)">
        Element 'element-citation': Unexpected element name.
      </assert>
      <assert test="not(etal)">
        Element 'element-citation': Unexpected element etal.
      </assert>
      <assert test="not(collab)">
        Element 'element-citation': Unexpected element collab.
      </assert>
    </rule>

    <rule context="//element-citation">
      <assert test="parent::ref">
        Unexpected element 'element-citation': Allowed only as child of ref elements.
      </assert>
    </rule>
  </pattern>

  <pattern id="person-group">
    <title>
      Make sure person-group-type is present.
    </title>

    <rule context="article/back/ref-list/ref/element-citation/person-group | 
                   article/front/article-meta/product/person-group">
      <assert test="@person-group-type">
        Element 'person-group': Missing attribute person-group-type.
      </assert>
    </rule>
  </pattern>

  <pattern id="person-group-type_values">
    <title>
      person-group/@person-group-type value constraints.
    </title>

    <rule context="article/back/ref-list/ref/element-citation/person-group[@person-group-type] | 
                   article/front/article-meta/product/person-group[@person-group-type]">
      <assert test="@person-group-type = 'author' or
                    @person-group-type = 'compiler' or 
                    @person-group-type = 'editor' or
                    @person-group-type = 'translator'">
        Element 'person-group', attribute person-group-type: Invalid value '<value-of select="@person-group-type"/>'.
      </assert>
    </rule>
  </pattern>

  <pattern id="fn_attributes">
    <title>
      Make sure some attributes are present
    </title>

    <rule context="article/front/article-meta/author-notes/fn | 
                   article/back/fn-group/fn">
      <assert test="@fn-type">
        Element 'fn': Missing attribute fn-type.
      </assert>
    </rule>
  </pattern>

  <pattern id="fn-group">
    <title>
      Make sure fn-type is valid against a white list.
    </title>

    <rule context="article/back/fn-group/fn[@fn-type]">
      <assert test="@fn-type = 'abbr' or
                    @fn-type = 'com' or 
                    @fn-type = 'financial-disclosure' or
                    @fn-type = 'supported-by' or
                    @fn-type = 'presented-at' or
                    @fn-type = 'supplementary-material' or
                    @fn-type = 'other'">
        Element 'fn', attribute fn-type: Invalid value '<value-of select="@fn-type"/>'.
      </assert>
    </rule>
    <rule context="article/front/article-meta/author-notes/fn[@fn-type]">
      <assert test="@fn-type = 'author' or
                    @fn-type = 'con' or
                    @fn-type = 'conflict' or
                    @fn-type = 'corresp' or
                    @fn-type = 'current-aff' or
                    @fn-type = 'deceased' or
                    @fn-type = 'edited-by' or 
                    @fn-type = 'equal' or
                    @fn-type = 'on-leave' or
                    @fn-type = 'participating-researchers' or
                    @fn-type = 'present-address' or
                    @fn-type = 'previously-at' or
                    @fn-type = 'study-group-members' or
                    @fn-type = 'other'">
        Element 'fn', attribute fn-type: Invalid value '<value-of select="@fn-type"/>'.
      </assert>
    </rule>
  </pattern>

  <pattern id="xhtml-table">
    <title>
      Tables should be fully tagged. tr elements are not supposed to be declared
      at toplevel.
    </title>

    <rule context="//table">
      <assert test="not(tr)">
        Element 'table': Unexpected element tr.
      </assert>
      <assert test="not(tbody//th)">
        Element 'table': Unexpected element th inside tbody.
      </assert>
      <assert test="not(thead//td)">
        Element 'table': Unexpected element td inside thead.
      </assert>
    </rule>
  </pattern>

  <pattern id="supplementary-material_mimetype">
    <title>
      The attributes mimetype and mime-subtype are required.
    </title>

    <rule context="article//supplementary-material">
      <assert test="@mimetype">
        Element 'supplementary-material': Missing attribute mimetype.
      </assert>
      <assert test="@mime-subtype">
        Element 'supplementary-material': Missing attribute mime-subtype.
      </assert>
    </rule>
  </pattern>

  <pattern id="article_attributes">
    <title>
      Make sure some attributes are present
    </title>

    <rule context="article">
      <assert test="@article-type">
        Element 'article': Missing attribute article-type.
      </assert>
      <assert test="@xml:lang">
        Element 'article': Missing attribute xml:lang.
      </assert>
      <assert test="@dtd-version">
        Element 'article': Missing attribute dtd-version.
      </assert>
      <assert test="@specific-use">
        Element 'article': Missing SPS version at the attribute specific-use.
      </assert>
    </rule>
  </pattern>

  <pattern id="article_article-type-values">
    <title>
      Allowed values for article/@article-type
    </title>

    <rule context="article[@article-type]">
      <assert test="@article-type = 'abstract' or 
                    @article-type = 'announcement' or
                    @article-type = 'other' or
                    @article-type = 'article-commentary' or 
                    @article-type = 'case-report' or 
                    @article-type = 'editorial' or
                    @article-type = 'correction' or
                    @article-type = 'letter' or 
                    @article-type = 'research-article' or
                    @article-type = 'in-brief' or 
                    @article-type = 'review-article' or 
                    @article-type = 'book-review' or 
                    @article-type = 'retraction' or 
                    @article-type = 'brief-report' or 
                    @article-type = 'rapid-communication' or 
                    @article-type = 'reply' or 
                    @article-type = 'translation'">
        Element 'article', attribute article-type: Invalid value '<value-of select="@article-type"/>'.
      </assert>
    </rule>
  </pattern>

  <pattern id="article_specific-use-values">
    <title>
      The SPS version must be declared in article/@specific-use 
    </title>

    <rule context="article[@specific-use]">
      <assert test="@specific-use = 'sps-1.1'">
        Element 'article', attribute specific-use: Invalid value '<value-of select="@specific-use"/>'.
      </assert>
    </rule>
  </pattern>

  <pattern id="named-content_attributes">
    <title>
      Make sure some attributes are present
    </title>

    <rule context="article/front/article-meta/aff/addr-line/named-content">
      <assert test="@content-type">
        Element 'named-content': Missing attribute content-type.
      </assert>
    </rule>
  </pattern>

  <pattern id="named-content_content-type-values">
    <title>
      Allowed values for named-content/@content-type
    </title>

    <rule context="article/front/article-meta/aff/addr-line/named-content[@content-type]">
      <assert test="@content-type = 'city' or
                    @content-type = 'state'">
        Element 'named-content', attribute content-type: Invalid value '<value-of select="@content-type"/>'.
      </assert>
    </rule>
  </pattern>

  <pattern id="month">
    <title>
      Only integers between 1 and 12.
    </title>

    <rule context="//month">
      <assert test="current() = '1' or current() = '01' or
                    current() = '2' or current() = '02' or
                    current() = '3' or current() = '03' or
                    current() = '4' or current() = '04' or
                    current() = '5' or current() = '05' or
                    current() = '6' or current() = '06' or
                    current() = '7' or current() = '07' or
                    current() = '8' or current() = '08' or
                    current() = '9' or current() = '09' or
                    current() = '10' or
                    current() = '11' or
                    current() = '12'">
        Element 'month': Invalid value '<value-of select="current()"/>'.
      </assert>
    </rule>
  </pattern>

  <pattern id="size_attributes">
    <title>
      Make sure some attributes are present
    </title>

    <rule context="article/front/article-meta/product/size | 
                   article/back/ref-list/ref/element-citation/size">
      <assert test="@units">
        Element 'size': Missing attribute units.
      </assert>
    </rule>
  </pattern>

  <pattern id="size_units-values">
    <title>
      Allowed values for size/@units
    </title>

    <rule context="article/front/article-meta/product/size[@units] | 
                   article/back/ref-list/ref/element-citation/size[@units]">
      <assert test="@units = 'pages'">
        Element 'size', attribute units: Invalid value '<value-of select="@units"/>'.
      </assert>
    </rule>
  </pattern>

  <pattern id="list_attributes">
    <title>
      Make sure some attributes are present
    </title>

    <rule context="//list">
      <assert test="@list-type">
        Element 'list': Missing attribute list-type.
      </assert>
    </rule>
  </pattern>

  <pattern id="list_list-type-values">
    <title>
      Allowed values for list/@list-type
    </title>

    <rule context="//list[@list-type]">
      <assert test="@list-type = 'order' or
                    @list-type = 'bullet' or
                    @list-type = 'alpha-lower' or
                    @list-type = 'alpha-upper' or
                    @list-type = 'roman-lower' or
                    @list-type = 'roman-upper' or
                    @list-type = 'simple'">
        Element 'list', attribute list-type: Invalid value '<value-of select="@list-type"/>'.
      </assert>
    </rule>
  </pattern>

  <pattern id="media_attributes">
    <title>
      Make sure some attributes are present
    </title>

    <rule context="//media">
      <assert test="@mime-subtype">
        Element 'media': Missing attribute mime-subtype.
      </assert>
      <assert test="@mimetype">
        Element 'media': Missing attribute mimetype.
      </assert>
      <assert test="@xlink:href">
        Element 'media': Missing attribute xlink:href.
      </assert>
    </rule>
  </pattern>

  <pattern id="ext-link_attributes">
    <title>
      Make sure some attributes are present. Also, the value of 
      ext-link-type is validated against a white-list.
    </title>

    <rule context="//ext-link">
      <assert test="@ext-link-type">
        Element 'ext-link': Missing attribute ext-link-type.
      </assert>
      <assert test="@ext-link-type = 'uri'">
        Element 'ext-link', attribute ext-link-type: Invalid value '<value-of select="@ext-link-type"/>'.
      </assert>
      <assert test="@xlink:href">
        Element 'ext-link': Missing attribute xlink:href.
      </assert>
    </rule>
  </pattern>

  <pattern id="ext-link_href_values">
    <title>
      When //ext-link/@ext-link-type="uri", @xlink:href must start with
      http:// or https://.
    </title>

    <rule context="//ext-link[@ext-link-type='uri']">
      <assert test="starts-with(@xlink:href, 'http://') or 
                    starts-with(@xlink:href, 'https://')">
        Element 'ext-link', attribute xlink:href: Missing HTTP URI scheme in '<value-of select="@xlink:href"/>'.
      </assert>
    </rule>
  </pattern>

  <pattern id="element-citation_attributes">
    <title>
      Make sure some attributes are present. 
    </title>

    <rule context="article/back/ref-list/ref/element-citation">
      <assert test="@publication-type">
        Element 'element-citation': Missing attribute publication-type.
      </assert>
    </rule>
  </pattern>

  <pattern id="element-citation_publication-type-values">
    <title>
      Allowed values for element-citation/@publication-type
    </title>

    <rule context="article/back/ref-list/ref/element-citation[@publication-type]">
      <assert test="@publication-type = 'journal' or
                    @publication-type = 'book' or
                    @publication-type = 'webpage' or
                    @publication-type = 'thesis' or
                    @publication-type = 'confproc' or
                    @publication-type = 'patent' or
                    @publication-type = 'report' or
                    @publication-type = 'software' or
                    @publication-type = 'legal-doc' or
                    @publication-type = 'newspaper' or
                    @publication-type = 'other' or
                    @publication-type = 'database'">
        Element 'element-citation', attribute publication-type: Invalid value '<value-of select="@publication-type"/>'.
      </assert>
    </rule>
  </pattern>
</schema>

