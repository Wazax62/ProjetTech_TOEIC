import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ReponsejusteComponent } from './reponsejuste.component';

describe('ReponsejusteComponent', () => {
  let component: ReponsejusteComponent;
  let fixture: ComponentFixture<ReponsejusteComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ReponsejusteComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ReponsejusteComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
