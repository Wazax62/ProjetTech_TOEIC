import { TestBed } from '@angular/core/testing';

import { FichierScannerService } from './fichier-scanner.service';

describe('FichierScannerService', () => {
  let service: FichierScannerService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(FichierScannerService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
