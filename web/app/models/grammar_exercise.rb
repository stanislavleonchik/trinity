class GrammarExercise < ApplicationRecord
  validates :raw_verb, presence: true
  validates :ready_verb, presence: true
  validates :sentence, presence: true
end
