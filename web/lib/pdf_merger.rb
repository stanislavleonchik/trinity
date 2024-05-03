require 'docx'
require 'prawn'
require 'combine_pdf'
module PdfMerger

  def self.merge_two_docs(doc1, doc2)

    comb = CombinePDF.new
    comb << CombinePDF.load(doc1)
    comb << CombinePDF.load(doc2)

    comb.to_pdf.force_encoding('BINARY')
  end

  def self.merge_one_doc(doc1)

    comb = CombinePDF.new
    comb << CombinePDF.load(doc1)

    comb.to_pdf.force_encoding('BINARY')
  end


end