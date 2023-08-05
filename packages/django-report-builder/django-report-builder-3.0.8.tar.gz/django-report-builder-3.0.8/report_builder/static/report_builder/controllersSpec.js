describe('Controller: ReportFilterCtrl', function() {
    var ctrl, scope, service;
    beforeEach(module('reportBuilderApp'));
    beforeEach(inject(function($rootScope, $controller) {
        scope = $rootScope.$new();
        ctrl = $controller('ReportFilterCtrl', {$scope: scope});
    }));
    it('should GO FUCK ITSELF', function() {
        expect('assfuck').toEqual('assfuck');
    });
});
