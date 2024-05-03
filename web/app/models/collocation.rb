class Collocation < ApplicationRecord
  validates :coloc, presence: true
  validates :count, presence: true, numericality: { only_integer: true }
  validates :translation, presence: true
end
