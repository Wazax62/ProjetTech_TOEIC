import { TestBed } from '@angular/core/testing';

import { ReponseetudiantService } from './reponseetudiant.service';

describe('ReponseetudiantService', () => {
  let service: ReponseetudiantService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ReponseetudiantService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
