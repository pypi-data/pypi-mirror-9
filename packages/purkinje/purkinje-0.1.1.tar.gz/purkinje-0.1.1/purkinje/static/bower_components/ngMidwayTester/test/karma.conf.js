module.exports = function(config) {
  config.set({
    basePath : '../',
    files : [
      'app/bower_components/angular/angular.js',
      './bower_components/angularjs/index.js',
      './bower_components/angularjs-route/index.js',
      './src/ngMidwayTester.js',
      './test/lib/chai.js',
      './test/spec/ngMidwayTesterSpec.js'
    ],
    singleRun: true,
    frameworks: ['mocha'],
    browsers: ['Chrome'],
    proxies: {
      '/': 'http://localhost:8844/'
    }
  });
};
