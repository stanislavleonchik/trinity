require 'json'
module ResponseConverter

  def self.get_doc_names_sorted(probas)

    labels_sorted = Rails.cache.read('labels_sorted')
    documents = Rails.cache.read('documents')

    probas = JSON.parse(probas)[0] # получаем одномерный массив из вероятностей


    indexed_probas = probas.map.with_index.to_a
    sorted_probas = indexed_probas.sort_by{ |el| -el.first }

    sorted_probas.map { |prob| documents[labels_sorted[prob.second]] }
  end

end