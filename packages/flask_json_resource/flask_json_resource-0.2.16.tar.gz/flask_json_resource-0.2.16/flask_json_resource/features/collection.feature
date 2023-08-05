Feature: Retrieve resources

    As an HTTP client 
    I want to retrieve collection resources

    Background:
        Given access to the API

    Scenario: Retrieve all message
        When I insert a message: {"title": "test-1", "content": "A message", "user_id": 1}
        And I insert a message: {"title": "test-2", "content": "A message", "user_id": 1}
        And I insert a message: {"title": "test-3", "content": "A message", "user_id": 1}
        And I insert a message: {"title": "test-4", "content": "A message", "user_id": 1}
        When I make a GET request to "/messages/"
        Then the response status should be 200
        And "/meta/found" should contain "4"
        And the size of "/items" should be 4
