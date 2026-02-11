import { TestBed } from '@angular/core/testing';

import { ReponseJusteService } from './reponsejuste.service';

describe('ReponsejusteService', () => {
  let service: ReponseJusteService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ReponseJusteService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
