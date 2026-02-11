import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AddSemestreComponent } from './add-semestre.component';

describe('AddSemestreComponent', () => {
  let component: AddSemestreComponent;
  let fixture: ComponentFixture<AddSemestreComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AddSemestreComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AddSemestreComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
