import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ScoreStudentComponent } from './score-student.component';

describe('ScoreStudentComponent', () => {
  let component: ScoreStudentComponent;
  let fixture: ComponentFixture<ScoreStudentComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ScoreStudentComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ScoreStudentComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
