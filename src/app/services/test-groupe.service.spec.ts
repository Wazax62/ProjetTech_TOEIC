import { TestBed } from '@angular/core/testing';

import { TestGroupeService } from './test-groupe.service';

describe('TestGroupeService', () => {
  let service: TestGroupeService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(TestGroupeService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
