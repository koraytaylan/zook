describe('TODO list', function() {
  it('should filter results', function() {

    // Find the element with ng-model="user" and type "jacksparrow" into it
    element(by.model('user')).sendKeys('jacksparrow');

    // Find the first (and only) button on the page and click it
    element(by.css(':button')).click();

    // Verify that there are 10 tasks
    expect(element.all(by.repeater('task in tasks')).count()).toEqual(10);

    // Enter 'groceries' into the element with ng-model="filterText"
    element(by.model('filterText')).sendKeys('groceries');

    // Verify that now there is only one item in the task list
    expect(element.all(by.repeater('task in tasks')).count()).toEqual(1);
  });
});