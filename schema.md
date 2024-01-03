# Database Schema

## Job Entity

- `job_id` (Primary Key)
- `job_logo` (Image field)
- `job_description` (text field)
- `job_link` (URL field)
- `company_name` (character field)
- `job_title` (character field)
- `location` (Character field)
- `time_added` (timestamp)
- `salary_range` (character field)
- `is_full_time` (boolean field)

## Talent Entity

- `talent_id` (Primary Key)
- `name` (character field)
- `timezone` (character field)
- `language` (character field)
- `about_me` (text field)
- `summary` (text field)
- `profile_visits` (positive integer field)
- `reviews_count`
- `average_rating`
- `email`
- `discord_profile`
- `twitter_profile`

## Review Entity

- `review_id` (Primary Key)
- `review`
- `reviewer_name`
- `occupation`
- `rating`
- `talent_id` (Foreign Key referencing Talent Entity)

## Experience Entity

- `experience_id` (Primary Key)
- `project_logo`
- `company_name`
- `role`
- `description`
- `start_date` (Month and Year)
- `end_date` (Month and Year)
- `currently_working`
- `verified`
- `twitter_link`
- `discord_link`
- `talent_id` (Foreign Key referencing Talent Entity)

### Relationships

- **Talent and Review:** One-to-Many relationship. A talent can have multiple reviews.
- **Talent and Experience:** One-to-Many relationship. A talent can have multiple experiences.
- **Review and Talent, Experience:** Each review and experience is linked to a specific talent.

### Utilities

- **Job Search Filters:**
  - `job_type`
  - `is_remote`

- **Talent Search Filters:**
  - `skills`
  - `timezone`

- **Sorting:**
  - Sort jobs and talents based on various attributes like date added, salary, rating, etc.

- **Search Results:**
  - Provide search results for jobs and talents along with count.
