import { TestBed } from '@angular/core/testing';


import { TestCreationService } from './testcreation.service';

describe('TestGroupeService', () => {
  let service: TestCreationService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(TestCreationService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
