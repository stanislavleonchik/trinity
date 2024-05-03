class DocumentsController < ApplicationController
  def new
    @doc_type = Rails.cache.read('documents').key(params[:name])
  end

  def download

    @doc_type = params[:type].to_i
    #if params[:plaintiff].present?
      case @doc_type
      when 1,2
        doc1 = 'public/doc_parts/шапка-' + params[:plaintiff] + '-' + params[:defendant] + '.pdf'
        case @doc_type
        when 1
          doc2 = 'public/doc_parts/иск-займ.pdf'
        when 2
          doc2 = 'public/doc_parts/иск-задолженность.pdf'
        else
          doc2 = 'public/doc_parts/иск-поставка.pdf'
        end
      when 3
        doc1 = 'public/doc_parts/заявление-аккредетив.pdf'
      when 4
        doc1 = 'public/doc_parts/заявление-преступление.pdf'
      else
        puts "error"
      end
    #end

    if doc2.present?
      send_data PdfMerger.merge_two_docs(doc1, doc2), filename: 'document.pdf', type: 'application/pdf', disposition: 'attachment'
    elsif doc1.present?
      #send_file doc1, filename: 'document.pdf', type: 'application/pdf', disposition: 'attachment'
      send_data PdfMerger.merge_one_doc(doc1), filename: 'document.pdf', type: 'application/pdf', disposition: 'attachment'
    end
  end

  private
  def document_params
    params.permit(:doc1, :doc2)
  end

end
