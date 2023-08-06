Feature: Retrieve resources

    As an HTTP client
    I want to create, retrieve, update and delete resources

    Background: Setup connection properties and data
        Given an existing message: {"title": "test", "content": "Singing in the shower", "user_id": 123}

    Scenario: Retrieve non-existing message
        When I set the "Accept" header to "application/json"
        And I set the "Content-type" header to "application/json"
        When I make a GET request to "/messages/does-not-exist"
        Then the response status should be 404

    Scenario: Retrieve existing message
        When I set the "Accept" header to "application/json"
        And I set the "Content-type" header to "application/json"
        When I make a GET request to "/messages/test/"
        Then the response status should be 200
        And the response data should be: {"title": "test", "content": "Singing in the shower", "user_id": 123}
        #And the "describedby" relation should be "/schemas/message.json"
        And the "user" relation should be "/users/123/"
        And the "create" relation should be "/messages/"
        And the "collection" relation should be "/messages/"
        And the "Content-type" header should be "application/json; profile=/schemas/message.json"

    Scenario: Delete a message
        When I set the "Accept" header to "application/json"
        And I set the "Content-type" header to "application/json"
        When I make a DELETE request to "/messages/test/"
        Then the response status should be 204

    Scenario: Get after delete message
        When I set the "Accept" header to "application/json"
        And I set the "Content-type" header to "application/json"
        When I make a DELETE request to "/messages/test/"
        When I make a GET request to "/messages/test/"
        Then the response status should be 404

    Scenario: Delete a non-existing message
        When I make a DELETE request to "/messages/does-not-exists/"
        Then the response status should be 404

    Scenario: PUT a message
        When I set the "Accept" header to "application/json"
        And I set the "Content-type" header to "application/json"
        When I make a PUT request to "/messages/test/" with data: {"title": "test", "content": "Another message", "user_id": 1}
        Then the response status should be 200
        And the response data should be: {"title": "test", "content": "Another message", "user_id": 1}

    Scenario: PUT a non-existing message
        When I set the "Accept" header to "application/json"
        And I set the "Content-type" header to "application/json"
        When I set the "Accept" header to "application/json"
        And I set the "Content-type" header to "application/json"
        When I make a PUT request to "/messages/does-not-exist/" with data: {"title": "does-not-exists", "content": "Another message", "user_id": 1}
        Then the response status should be 404

    Scenario: PUT an invalid message
        When I set the "Accept" header to "application/json"
        And I set the "Content-type" header to "application/json"
        When I make a PUT request to "/messages/test/" with data: {"content": "Another message", "user_id": "not-an-number"}
        Then the response status should be 422

    Scenario: PUT an invalid json
        When I set the "Accept" header to "application/json"
        And I set the "Content-type" header to "application/json"
        When I make a PUT request to "/messages/test/" with data: {"content": "Another message"
        Then the response status should be 400

    Scenario: POST a message
        When I set the "Accept" header to "application/json"
        And I set the "Content-type" header to "application/json"
        When I make a POST request to "/messages/" with data: {"title": "new", "content": "An new message", "user_id": 1}
        Then the response status should be 201
        And the response data should be: {"title": "new", "content": "An new message", "user_id": 1}
        And the "Location" header should be "/messages/new/"

    Scenario: POST a message that already exists
        When I set the "Accept" header to "application/json"
        And I set the "Content-type" header to "application/json"
        When I make a POST request to "/messages/" with data: {"title": "test", "content": "Another message", "user_id": 1}
        Then the response status should be 409

    Scenario: POST an invalid message
        When I set the "Accept" header to "application/json"
        And I set the "Content-type" header to "application/json"
        When I make a POST request to "/messages/" with data: {"content": "Another message", "user_id": 1}
        Then the response status should be 422

    Scenario: POST an invalid json message
        When I set the "Accept" header to "application/json"
        And I set the "Content-type" header to "application/json"
        When I make a POST request to "/messages/" with data: {"content": "Another message"
        Then the response status should be 400
