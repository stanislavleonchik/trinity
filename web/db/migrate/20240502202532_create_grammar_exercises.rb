class CreateGrammarExercises < ActiveRecord::Migration[7.1]
  def change
    create_table :grammar_exercises do |t|
      t.string :raw_verb
      t.string :ready_verb
      t.string :sentence

      t.timestamps
    end
  end
end
