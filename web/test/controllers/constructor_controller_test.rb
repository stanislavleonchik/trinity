require "test_helper"

class ConstructorControllerTest < ActionDispatch::IntegrationTest
  test "should get all" do
    get constructor_all_url
    assert_response :success
  end
end
