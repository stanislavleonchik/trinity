class CreateCollocations < ActiveRecord::Migration[7.1]
  def change
    create_table :collocations do |t|
      t.string :coloc
      t.integer :count
      t.string :translation

      t.timestamps
    end
  end
end
